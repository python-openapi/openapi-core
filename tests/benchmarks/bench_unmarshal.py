#!/usr/bin/env python3
"""Benchmark for SchemaUnmarshaller.unmarshal on a schema that exercises
nested objects, arrays, and composition (oneOf / allOf).

This is the code path that the `feature/validation-context` branch
modifies: validation now builds a `ValidationState` that the unmarshaller
reuses, so we expect changes to show up here.
"""

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

from openapi_core.unmarshalling.schemas import (
    oas30_write_schema_unmarshallers_factory,
)


@dataclass(frozen=True)
class Result:
    items: int
    repeats: int
    warmup: int
    seconds: List[float]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "items": self.items,
            "repeats": self.repeats,
            "warmup": self.warmup,
            "seconds": self.seconds,
            "median_s": statistics.median(self.seconds),
            "mean_s": statistics.mean(self.seconds),
            "stdev_s": statistics.pstdev(self.seconds),
            "ops_per_sec_median": self.items / statistics.median(self.seconds),
        }


# A schema with: nested object, array of objects, oneOf, allOf.
# Mirrors realistic API payloads where the validation-context refactor
# should pay off (we avoid re-resolving composed schemas at unmarshal time).
SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
        "address": {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "city": {"type": "string"},
                "zip": {"type": "string"},
            },
        },
        "contact": {
            "oneOf": [
                {
                    "type": "object",
                    "properties": {
                        "kind": {"type": "string"},
                        "email": {"type": "string"},
                    },
                    "required": ["kind", "email"],
                },
                {
                    "type": "object",
                    "properties": {
                        "kind": {"type": "string"},
                        "phone": {"type": "string"},
                    },
                    "required": ["kind", "phone"],
                },
            ]
        },
        "audit": {
            "allOf": [
                {
                    "type": "object",
                    "properties": {
                        "created_by": {"type": "string"},
                    },
                },
                {
                    "type": "object",
                    "properties": {
                        "created_at": {"type": "string"},
                    },
                },
            ]
        },
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "sku": {"type": "string"},
                    "qty": {"type": "integer"},
                    "price": {"type": "number"},
                },
            },
        },
    },
}

SPEC: Dict[str, Any] = {
    "openapi": "3.0.0",
    "info": {"title": "bench", "version": "0"},
    "paths": {},
}


def build_values(n: int, seed: int) -> List[Dict[str, Any]]:
    rnd = random.Random(seed)
    out: List[Dict[str, Any]] = []
    for i in range(n):
        # Alternate the oneOf branch so both are exercised.
        if i % 2 == 0:
            contact = {"kind": "email", "email": f"u{i}@example.com"}
        else:
            contact = {"kind": "phone", "phone": f"+1-555-{i:04d}"}
        out.append(
            {
                "id": i,
                "name": f"item-{i}",
                "tags": [f"t{rnd.randrange(100)}" for _ in range(5)],
                "address": {
                    "street": f"{rnd.randrange(9999)} Main St",
                    "city": "Springfield",
                    "zip": f"{rnd.randrange(99999):05d}",
                },
                "contact": contact,
                "audit": {
                    "created_by": "alice",
                    "created_at": "2026-01-01T00:00:00Z",
                },
                "items": [
                    {
                        "sku": f"sku-{rnd.randrange(10_000)}",
                        "qty": rnd.randrange(100),
                        "price": rnd.random() * 100,
                    }
                    for _ in range(4)
                ],
            }
        )
    return out


def run_once(unmarshaller: Any, values: List[Dict[str, Any]]) -> float:
    t0 = time.perf_counter()
    for v in values:
        unmarshaller.unmarshal(v)
    return time.perf_counter() - t0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", type=int, default=2000)
    ap.add_argument("--repeats", type=int, default=7)
    ap.add_argument("--warmup", type=int, default=2)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--output", type=str, default="")
    ap.add_argument("--no-gc", action="store_true")
    args = ap.parse_args()

    spec = SchemaPath.from_dict(SPEC)
    schema = SchemaPath.from_dict(SCHEMA)
    unmarshaller = oas30_write_schema_unmarshallers_factory.create(
        spec, schema
    )

    values = build_values(args.items, args.seed)

    if args.no_gc:
        gc.disable()

    for _ in range(args.warmup):
        run_once(unmarshaller, values)

    seconds: List[float] = []
    for _ in range(args.repeats):
        seconds.append(run_once(unmarshaller, values))

    if args.no_gc:
        gc.enable()

    result = Result(
        items=args.items,
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
