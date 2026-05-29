#!/usr/bin/env python3
"""Benchmark: canonical-path keying vs id(content) keying vs per-route
(navigation-path) keying for the SchemaValidator static-analysis caches.

Reports, per strategy:
  * cold_us_per_node -- cost of deriving the cache key for every schema
    node (the once-per-construction work).
  * warm_us_per_node -- steady-state derive+lookup cost (the hot path).
  * distinct_keys / dedup_ratio -- how many cache slots the strategy
    produces; higher dedup = fewer recomputations of needs_state.

"per_route" is the master/baseline behaviour (key on the navigation
SchemaPath, no $ref collapsing). "canonical" requires jsonschema-path
PR #263. "id_content" mirrors docs/plans/v3-cache-refactor/_caches.py.
"""

from __future__ import annotations

import argparse
import gc
import json
import statistics
import time
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from jsonschema_path import SchemaPath

HAS_CANONICAL = hasattr(SchemaPath, "canonical")


def build_spec(schemas: int, depth: int, shared_targets: int) -> SchemaPath:
    defs: dict[str, Any] = {
        f"Leaf{t}": {"type": "string", "format": "uuid"}
        for t in range(shared_targets)
    }
    components: dict[str, Any] = {}
    for s in range(schemas):
        node: dict[str, Any] = {"type": "object", "properties": {}}
        cursor = node["properties"]
        for d in range(depth):
            child: dict[str, Any] = {"type": "object", "properties": {}}
            cursor[f"level{d}"] = child
            cursor = child["properties"]
        for k in range(4):
            target = f"Leaf{(s + k) % shared_targets}"
            cursor[f"leaf{k}"] = {"$ref": f"#/$defs/{target}"}
        components[f"Schema{s}"] = node
    spec_dict = {
        "openapi": "3.1.0",
        "info": {"title": "bench-canonical", "version": "0"},
        "$defs": defs,
        "components": {"schemas": components},
    }
    return SchemaPath.from_dict(spec_dict)


def collect_schema_paths(spec: SchemaPath) -> list[SchemaPath]:
    paths: list[SchemaPath] = []

    def walk(node: SchemaPath) -> None:
        paths.append(node)
        if "properties" in node:
            for name, sub in (node / "properties").items():
                if isinstance(name, str):
                    walk(sub)

    for name, schema in (spec / "components" / "schemas").items():
        if isinstance(name, str):
            walk(schema)
    return paths


def key_per_route(path: SchemaPath) -> Any:
    return path  # master/baseline: navigation path identity


def key_canonical(path: SchemaPath) -> tuple[int, tuple[Any, ...]] | None:
    from referencing.exceptions import Unresolvable

    try:
        canon = path.canonical()
    except Unresolvable:
        return None
    return (id(canon.accessor), tuple(canon.parts))


def key_id_content(path: SchemaPath) -> int | None:
    try:
        with path.resolve() as resolved:
            return id(resolved.contents)
    except Exception:
        return None


@dataclass
class StrategyResult:
    name: str
    nodes: int
    distinct_keys: int
    cold_seconds: list[float] = field(default_factory=list)
    warm_seconds: list[float] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        cold = statistics.median(self.cold_seconds)
        warm = statistics.median(self.warm_seconds)
        return {
            "name": self.name,
            "nodes": self.nodes,
            "distinct_keys": self.distinct_keys,
            "dedup_ratio": round(self.nodes / self.distinct_keys, 2),
            "cold_us_per_node": round(cold / self.nodes * 1e6, 3),
            "warm_us_per_node": round(warm / self.nodes * 1e6, 3),
        }


def measure(name, paths, keyfn, repeats, warmup) -> StrategyResult:
    cold: list[float] = []
    distinct = 0
    for _ in range(repeats):
        seen = set()
        t0 = time.perf_counter()
        for p in paths:
            k = keyfn(p)
            if k is not None:
                seen.add(k)
        cold.append(time.perf_counter() - t0)
        distinct = len(seen)
    cache: dict[Any, bool] = {}
    for p in paths:
        k = keyfn(p)
        if k is not None:
            cache[k] = True
    for _ in range(warmup):
        for p in paths:
            cache.get(keyfn(p))
    warm: list[float] = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        for p in paths:
            cache.get(keyfn(p))
        warm.append(time.perf_counter() - t0)
    return StrategyResult(name, len(paths), distinct, cold, warm)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--schemas", type=int, default=500)
    ap.add_argument("--depth", type=int, default=3)
    ap.add_argument("--shared-targets", type=int, default=16)
    ap.add_argument("--repeats", type=int, default=7)
    ap.add_argument("--warmup", type=int, default=2)
    ap.add_argument("--output", type=str, default="")
    ap.add_argument("--no-gc", action="store_true")
    args = ap.parse_args()

    spec = build_spec(args.schemas, args.depth, args.shared_targets)
    paths = collect_schema_paths(spec)
    if args.no_gc:
        gc.disable()
    results = [
        measure("per_route", paths, key_per_route, args.repeats, args.warmup),
        measure(
            "id_content", paths, key_id_content, args.repeats, args.warmup
        ),
    ]
    if HAS_CANONICAL:
        results.append(
            measure(
                "canonical", paths, key_canonical, args.repeats, args.warmup
            )
        )
    if args.no_gc:
        gc.enable()
    payload = {
        "config": {
            "schemas": args.schemas,
            "depth": args.depth,
            "shared_targets": args.shared_targets,
            "nodes": len(paths),
            "has_canonical": HAS_CANONICAL,
        },
        "strategies": [r.as_dict() for r in results],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
