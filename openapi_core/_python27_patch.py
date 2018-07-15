import functools
try:
    from functools import lru_cache

except ImportError:
    from backports.functools_lru_cache import lru_cache
    functools.lru_cache = lru_cache

try:
    from functools import partialmethod

except ImportError:
    from backports.functools_partialmethod import partialmethod
    functools.partialmethod = partialmethod
