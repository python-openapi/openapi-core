#!/usr/bin/env python3
import argparse
import gc
import json
import random
import statistics
import time
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List

from jsonschema_path import SchemaPath

from openapi_core.templating.paths.finders import APICallPathFinder


@dataclass(frozen=True)
class Result:
    paths: int
    templates_ratio: float
    lookups: int
    repeats: int
    warmup: int
    seconds: List[float]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "paths": self.paths,
            "templates_ratio": self.templates_ratio,
            "lookups": self.lookups,
            "repeats": self.repeats,
            "warmup": self.warmup,
            "seconds": self.seconds,
            "median_s": statistics.median(self.seconds),
            "mean_s": statistics.mean(self.seconds),
            "stdev_s": statistics.pstdev(self.seconds),
            "ops_per_sec_median": self.lookups
            / statistics.median(self.seconds),
        }


def build_spec(paths: int, templates_ratio: float) -> SchemaPath:
    # Mix of exact and templated paths.
    # Keep it minimal so we measure finder cost, not schema complexity.
    tmpl = int(paths * templates_ratio)
    exact = paths - tmpl

    paths_obj: Dict[str, Any] = {}

    # Exact paths (fast case)
    for i in range(exact):
        p = f"/resource/{i}/sub"
        paths_obj[p] = {"get": {"responses": {"200": {"description": "ok"}}}}

    # Template paths (slow case)
    for i in range(tmpl):
        p = f"/resource/{i}" + "/{item_id}/sub/{sub_id}"
        paths_obj[p] = {"get": {"responses": {"200": {"description": "ok"}}}}

    spec_dict = {
        "openapi": "3.0.0",
        "info": {"title": "bench", "version": "0"},
        "servers": [{"url": "http://example.com"}],
        "paths": paths_obj,
    }
    return SchemaPath.from_dict(spec_dict)


def build_urls(
    paths: int, templates_ratio: float, lookups: int, seed: int
) -> List[str]:
    rnd = random.Random(seed)
    tmpl = int(paths * templates_ratio)
    exact = paths - tmpl

    urls: List[str] = []
    for _ in range(lookups):
        # 50/50 choose from each population, weighted by how many exist
        if tmpl > 0 and (exact == 0 or rnd.random() < (tmpl / paths)):
            i = rnd.randrange(tmpl)  # matches template bucket
            item_id = rnd.randrange(1_000_000)
            sub_id = rnd.randrange(1_000_000)
            urls.append(
                f"http://example.com/resource/{i}/{item_id}/sub/{sub_id}"
            )
        else:
            i = rnd.randrange(exact) if exact > 0 else 0
            urls.append(f"http://example.com/resource/{i}/sub")
    return urls


def run_once(finder: APICallPathFinder, urls: List[str]) -> float:
    t0 = time.perf_counter()
    for u in urls:
        finder.find("get", u)
    return time.perf_counter() - t0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paths", type=int, default=2000)
    ap.add_argument("--templates-ratio", type=float, default=0.6)
    ap.add_argument("--lookups", type=int, default=100_000)
    ap.add_argument("--repeats", type=int, default=7)
    ap.add_argument("--warmup", type=int, default=2)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--output", type=str, default="")
    ap.add_argument("--no-gc", action="store_true")
    args = ap.parse_args()

    spec = build_spec(args.paths, args.templates_ratio)
    finder = APICallPathFinder(spec)

    urls = build_urls(
        args.paths, args.templates_ratio, args.lookups, args.seed
    )

    if args.no_gc:
        gc.disable()

    # Warmup (JIT-less, but warms caches, alloc patterns, etc.)
    for _ in range(args.warmup):
        run_once(finder, urls)

    seconds: List[float] = []
    for _ in range(args.repeats):
        seconds.append(run_once(finder, urls))

    if args.no_gc:
        gc.enable()

    result = Result(
        paths=args.paths,
        templates_ratio=args.templates_ratio,
        lookups=args.lookups,
        repeats=args.repeats,
        warmup=args.warmup,
        seconds=seconds,
    )

    payload = result.as_dict()
    print(json.dumps(payload, indent=2, sort_keys=True))

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
