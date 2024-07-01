
from loguru import logger
import time


BASEFILEPATH = "C:/Users/ander/Documents/GitHub/Financial-Analyzer/src"  # tag:hardcode


def logfn(fn):
    from functools import wraps

    @wraps(fn)
    def wrapper(*args, **kwargs):
        logger.info(f"Starting function \"{fn.__name__}\" with args {locals()['args']} and kwargs {locals()['kwargs']}")

        start = round(time.time() * 1000)
        out = fn(*args, **kwargs)
        end = round(time.time() * 1000)

        timer = end - start
        logger.info(f"Done running function \"{fn.__name__}\" with return value {out} in {timer if timer > 0 else 0}ms")
        return out

    return wrapper