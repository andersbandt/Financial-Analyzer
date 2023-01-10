from functools import wraps
import time
def timer(func):
    """
    Times function calls.
    Place as a decorator over a function or class method
    and it will print out how long it took that function to execute.
    """
    @wraps(func)
    def _time_it(*args, **kwargs):
        start = int(round(time.time() * 1000))
        try:
            return func(*args, **kwargs)
        finally:
            end_ = int(round(time.time() * 1000)) - start
            print(f"Total execution time of {str(func)}: {end_ if end_ > 0 else 0} ms\n")
    return _time_it