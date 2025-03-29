import inspect
from os.path import isdir
from functools import wraps


class NotADirException(Exception):
    def __init__(self, error_path: str):
        self.path = error_path
        super().__init__("Not a directory: {}".format(error_path))


def ensure_folders(param_names):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            for param in param_names:
                if not isdir(bound_args.arguments[param]):
                    raise NotADirException(bound_args.arguments[param])
            return func(*args, **kwargs)
        return wrapper
    return decorator


if __name__ == '__main__':
    # Test the decorator
    @ensure_folders(['dir1', 'dir2'])
    def test_function(dir1, dir2):
        print(f"Directories: {dir1}, {dir2}")


    # Example usage
    test_function('/path/to/dir1', '/path/to/dir2')  # This should work if both are directories
