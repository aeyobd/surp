from functools import wraps
from numbers import Real


def isreal(param):
    """Validates if the given parameter is real"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if param not in kwargs:
                raise ValueError(f"Parameter not in function kwargs: {param}")
            if not isinstance(kwargs[param], Real):
                raise ValueError(f"Parameter {param} must be real, got {kwargs[param]}")
                
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate(param, condition, is_real=True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if param not in kwargs:
                raise ValueError(f"Parameter not in function kwargs: {param}")
            if condition(kwargs[param]):
                raise ValueError(f"validation failed for {param} = {kwargs[param]}")
                
            return func(*args, **kwargs)
        return wrapper
    return decorator


def arg_isreal(arg=0):
    """Checks if the given argument of the function is real"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            val = args[arg]
            if not isinstance(arg, Real):
                raise TypeError(f"argument must be a number, got {type(other).__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator
