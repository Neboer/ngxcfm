from os.path import sep
from typing import Literal

from ..log import logger


def current_os() -> Literal["win", "posix"]:
    return 'win' if sep == '\\' else 'posix'


def assert_valid_style(style: str):
    if style not in ['win', 'posix']:
        logger.error("Unknown style, please specify 'win' or 'posix'.")
        raise ValueError("Unknown style, please specify 'win' or 'posix'.")

def optional_style_default_current_os(func):
    def wrapper(*args, **kwargs):
        import inspect
        sig = inspect.signature(func)
        pos_args = dict(zip(sig.parameters.keys(), args))
        if 'style' not in kwargs and ('style' not in pos_args or pos_args['style'] is None):
            kwargs['style'] = current_os()
        return func(*args, **kwargs)
    return wrapper
