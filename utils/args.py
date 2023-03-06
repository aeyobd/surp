from functools import wraps
from functools import singledispatch


@singledispatch
def check_arg(func, arg_name, condition=True):

    @wraps
    def inner(func, args, **kwargs):
        pass
