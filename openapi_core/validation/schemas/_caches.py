"""Per-resolver schema-property caches.

Several ``SchemaValidator`` methods need to answer static questions
about a schema -- "does this subtree carry composition?" or "does this
subtree contain a binary/byte string?" -- and reuse the answers across
many validation calls. A naive class-level cache keyed on ``SchemaPath``
is unsafe because ``SchemaPath`` equality / hashing (inherited from
``pathable.BasePath``) is path-only: two distinct OpenAPI specs that
happen to share a JSON-pointer path (``anyOf#0``) collide.

This module provides a small key abstraction that keeps the answers
correct across specs and lets them be reclaimed when the spec is
garbage-collected.

Design:

* Each OpenAPI spec resolves through a single, stable ``Resolver``
  instance. All ``SchemaPath`` objects derived from the same root spec
  share that resolver, so the resolver's identity is a reliable
  per-spec key (verified empirically against ``jsonschema-path``).
* Each spec's content is laid out as a single tree of dict objects.
  Two distinct dicts within the same spec have distinct ``id()``
  values, and the ``id()`` is stable for the lifetime of the dict
  (it is a CPython memory address). Within a spec, ``id(content)``
  is therefore safe as an inner cache key.
* When the spec (and its resolver) is collected, ``weakref.finalize``
  evicts the entire spec's cache slot in one shot. This both prevents
  the cache from pinning the spec in memory and forecloses on the
  classic ``id()``-reuse hazard.

The module exposes one helper per query: ``ResolverScopedCache.get`` /
``put``. Callers are responsible for the actual computation -- the
cache only stores results.
"""

from __future__ import annotations

import weakref
from typing import Any
from typing import Dict
from typing import Optional


class _PerResolverCache:
    """One spec's worth of cached answers.

    ``slots`` reduces the per-spec overhead to two dict slots; we
    expect at most a handful of these to exist concurrently (one per
    loaded OpenAPI document).
    """

    __slots__ = ("needs_state", "needs_binary_normalization")

    def __init__(self) -> None:
        self.needs_state: Dict[int, bool] = {}
        self.needs_binary_normalization: Dict[int, bool] = {}


# Class-level registry of per-resolver caches. Keys are ``id(resolver)``
# and entries are removed via ``weakref.finalize`` when the resolver is
# collected; ``id()`` reuse is therefore safe by construction (the slot
# is empty before the next resolver can claim the address).
_caches: Dict[int, _PerResolverCache] = {}


def cache_for(resolver: Any) -> _PerResolverCache:
    """Return the per-resolver cache for ``resolver``, creating it on
    first access. Registers a finalizer so the entry evicts when the
    resolver is collected.
    """
    rid = id(resolver)
    cache = _caches.get(rid)
    if cache is not None:
        return cache
    cache = _PerResolverCache()
    _caches[rid] = cache
    # ``weakref.finalize`` is the only mechanism that survives the
    # resolver's collection. The callback pops by the resolver's *old*
    # id, which is correct: the slot was claimed by this resolver and
    # nothing else can occupy it until this callback fires.
    weakref.finalize(resolver, _caches.pop, rid, None)
    return cache


def _reset_for_tests() -> None:
    """Drop all cached entries. Test-only helper; production code never
    needs to call this because the resolver lifetime drives eviction.
    """
    _caches.clear()


__all__ = ["cache_for", "_PerResolverCache", "_reset_for_tests"]
