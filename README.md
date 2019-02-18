# Cache Manager

A minimalistic pickle based cache manager for your long and computationally expensive functions. 

## Examples

The easiest way to use cache_manager is through its `memoize` decorator:

```python
from cache_manager import CacheManager

cache_manager = CacheManager("/data/.cache") # path to a cache folder


#The string passed to the decorator will be hashed and used as key to retrieve cached values.
@cache_manager.memoize("expensive_function_a_b")
def expensive_function(a, b):
    # do something very long...
    return c
    
# Run the expensive function a first time
result = expensive_function(a, b) # this is very long...

# Run it again
result = expensive_function(a, b) # this value is now loaded from cache.
```

Alternatively the cache_manager API provide you with a `cachify` method that allow to cache any methods execution:

```python
def expensive_function(a, b):
    # do something very long...
    return c

#Run the expensive function a first time
result = cache_manager.cachify('expensive_function_a_b', expensive_function, a, b)

#Run it again (this is cached this time)
result = cache_manager.cachify('expensive_function_a_b', expensive_function, a, b)
```