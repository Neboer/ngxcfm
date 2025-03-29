from os.path import sep
from typing import Literal
import inspect
from functools import wraps
from ..log import logger


def current_os() -> Literal["win", "posix"]:
    return 'win' if sep == '\\' else 'posix'


def assert_valid_style(style: str):
    if style not in ['win', 'posix']:
        logger.error("Unknown style, please specify 'win' or 'posix'.")
        raise ValueError("Unknown style, please specify 'win' or 'posix'.")

def optional_style_default_current_os(func):
    @wraps(func, assigned=())
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        pos_args = dict(zip(sig.parameters.keys(), args))
        if 'style' not in kwargs and ('style' not in pos_args or pos_args['style'] is None):
            kwargs['style'] = current_os()
        return func(*args, **kwargs)
    return wrapper

if __name__ == '__main__':
    # Test the decorator
    @optional_style_default_current_os
    def test_function(style: str = None):
        print(f"Style: {style}")

    # Example usage
    test_function()  # This should work if both are directories
    test_function('win')
    test_function('posix')