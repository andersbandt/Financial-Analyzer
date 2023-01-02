from loguru import logger


def logfn(fn):
    from functools import wraps

    @wraps(fn)
    def wrapper(*args, **kwargs):
        logger.info(f"About to run {fn.__name__} with args {locals()}")

        out = fn(*args, **kwargs)

        logger.info(f"Done running {fn.__name__} with return value {out}")
        return out

    return wrapper
