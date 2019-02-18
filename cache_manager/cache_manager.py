from typing import Callable, TypeVar, Iterable, Mapping, Any
from hashlib import sha256
from os.path import isfile, isdir,join
from os import getcwd, remove
from functools import wraps
import pickle
import time

T = TypeVar("T")


class CacheManager:
    """Cache the executions result of your methods using pickle.

    Examples:
        def very_long_method(arg_a, arg_b):
            return return_value

        return_value = cache_manager.cachify('very_long_method_name', very_long_method, arg_a, arg_b)
    """
    def __init__(self, cache_folder_path: str) -> None:
        """Initialize the cache manager.

        :param cache_folder_path: Path to the folder in which the cache files will be saved.
        """
        assert isdir(cache_folder_path)
        self.cache_folder_path = cache_folder_path

    @staticmethod
    def str_to_hash(str_to_hash: str) -> str:
        """Hash a string into a unique hash representation.

        :param str_to_hash: the string to hash.
        :return: a unique hash for each given input.
        """
        return sha256(str_to_hash.encode("utf8")).hexdigest()

    def str_to_filename(self, str_to_hash: str) -> str:
        """Convert a string into a cache file filename.

        :param str_to_hash: the unique string representation of the operation to be cached.
        :return: the corresponding filename.
        """
        return self.str_to_hash(str_to_hash) + ".pickle"

    def has_in_cache(self, str_to_hash: str) -> bool:
        """Return True if the hash is found, False if not found.

        :param str_to_hash: the unique string representation of the operation to cache.
        :return: True if cached, False otherwise
        """
        return isfile(join(self.cache_folder_path, self.str_to_filename(str_to_hash)))

    def retrieve_from_cache(self, str_to_hash: str) -> T:
        """Return the object defined by `str_to_hash` from cache.

        :param str_to_hash: the unique string representation of the operation cached.
        :return: object by `str_to_hash`.
        """
        with open(join(self.cache_folder_path, self.str_to_filename(str_to_hash)), mode="rb") as f:
            return pickle.load(f)

    def clear_from_cache(self, str_to_hash: str) -> None:
        """Clear an object from the cache.

        :param str_to_hash: he unique string representation of the operation cached.
        :return: None
        """
        remove(join(self.cache_folder_path, self.str_to_filename(str_to_hash)))

    def put_in_cache(self, str_to_hash: str, obj_to_cache: T) -> None:
        """Put an object in cache.

        :param str_to_hash: the unique string representation of the operation cached.
        :param obj_to_cache: the value to cache.
        :return: None
        """
        with open(join(self.cache_folder_path, self.str_to_filename(str_to_hash)), mode="wb") as f:
            pickle.dump(obj_to_cache, f)

    def cachify(self, str_to_hash: str, func: Callable[..., T], *args: Iterable[Any], **kwargs: Mapping[Any, Any]) -> T:
        """Cachify a given method and return result either from cache or from previous run.

        :param str_to_hash: a unique string corresponding to the operation to cachify.
        :param func: the function that will be executed if no cache values are found.
        :param args: the arguments for `func`.
        :return: returns the results of the `func` function
        """
        if self.has_in_cache(str_to_hash):
            return self.retrieve_from_cache(str_to_hash)
        else:
            return_value = func(*args, **kwargs)
            self.put_in_cache(str_to_hash, return_value)
            return return_value

    def memoize(self, str_to_hash: str) -> Callable[..., Callable[..., T]]:
        """Decorator function that memorize in cache the function decorated.

        :param str_to_hash: the unique string representation of the operation that will be hashed.
        :return: the actual decorator function.
        """
        def decorator_memoize(func: Callable[..., T]) -> Callable[..., T]:
            """Actual definition of the decorator function.

            :param func: the function decorated.
            :return: a wrapper function around `func` .
            """
            @wraps(func)
            def wrapper(*args: Iterable[Any], **kwargs: Mapping[Any, Any]) -> T:
                """Simple wrapper function that cachify `func`."""
                return self.cachify(str_to_hash, func, *args, **kwargs)
            return wrapper
        return decorator_memoize


if __name__ == "__main__":

    # -- Config / required variables for tests

    some_folder_path = getcwd()
    cache_manager = CacheManager(some_folder_path)

    def expensive_function(a: str, b: str, c: str) -> str:
        time.sleep(1)
        return a + b + c


    # Examples of sha256 mapping to test the hashing function
    str_hash_mapping = {
        'cache_manager': '34d7518f35fb588fcc7768ea21389b823f33e8eb8742a34172fcfff5ec388409',
        'test': '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
        'abc': 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
    }

    # -- Tests

    def test_str_to_hash() -> bool:
        for key, value in str_hash_mapping.items():
            if cache_manager.str_to_hash(key) != value:
                return False
        return True

    def test_str_to_filename() -> bool:
        for key, value in str_hash_mapping.items():
            if cache_manager.str_to_filename(key) != value + ".pickle":
                return False
        return True

    def test_has_in_cache() -> bool:
        for key in str_hash_mapping.keys():
            cache_manager.put_in_cache(key, "a")
            if not cache_manager.has_in_cache(key):
                return False
            cache_manager.clear_from_cache(key)
            if cache_manager.has_in_cache(key):
                return False
        return True

    def test_retrieve_from_cache() -> bool:
        for key in str_hash_mapping.keys():
            obj = "test"
            cache_manager.put_in_cache(key, obj)
            retrieved_obj = cache_manager.retrieve_from_cache(key)
            if obj != retrieved_obj:
                return False
            cache_manager.clear_from_cache(key)
        return True

    def test_clear_from_cache() -> bool:
        for key in str_hash_mapping.keys():
            obj = "test"
            cache_manager.put_in_cache(key, obj)
            cache_manager.clear_from_cache(key)
            if cache_manager.has_in_cache(key):
                return False
        return True

    def test_put_in_cache() -> bool:
        for key in str_hash_mapping.keys():
            obj = "test"
            cache_manager.put_in_cache(key, obj)
            if not cache_manager.has_in_cache(key):
                return False
            cache_manager.clear_from_cache(key)
        return True

    def test_cachify() -> bool:
        a = "Hello"
        b = " "
        c = "World!"

        start = time.time()
        first_expensive_result = cache_manager.cachify('expensive_name', expensive_function, a, b, c)
        end = time.time()
        first_run_time = end - start

        print("First run took {}s".format(first_run_time))

        start = time.time()
        second_expensive_result = cache_manager.cachify('expensive_name', expensive_function, a, b, c)
        end = time.time()
        second_run_time = end - start

        print("Second run took {}s".format(second_run_time))

        cache_manager.clear_from_cache('expensive_name')

        if first_expensive_result != second_expensive_result or second_run_time > first_run_time:
            return False

        return True

    def test_memoize() -> bool:
        a = "Hello"
        b = " "
        c = "World!"

        @cache_manager.memoize("expensive_name")
        def expensive_function_memoized(a_: str, b_: str, c_: str) -> str:
            time.sleep(1)
            return a_ + b_ + c_

        start = time.time()
        first_expensive_result = expensive_function_memoized(a, b, c)
        end = time.time()
        first_run_time = end - start

        print("First run of the memoized function took {}s".format(first_run_time))

        start = time.time()
        second_expensive_result = expensive_function_memoized(a, b, c)
        end = time.time()
        second_run_time = end - start

        print("Second run of the memoized function took {}s".format(second_run_time))

        cache_manager.clear_from_cache('expensive_name')

        if first_expensive_result != second_expensive_result or second_run_time > first_run_time:
            return False

        return True

    print("Running all unit tests...")
    assert test_str_to_hash()
    assert test_str_to_filename()
    assert test_has_in_cache()
    assert test_retrieve_from_cache()
    assert test_put_in_cache()
    assert test_cachify()
    assert test_memoize()
    print("Done. All test passed !")
