# symlink 在Windows中的作用非常奇怪，这个函数的作用旨在规范这个问题。
from os import walk, readlink, remove, symlink
from os.path import exists, isfile, join, isabs, islink, relpath, dirname, basename, normpath, sep
import posixpath as ix_path
from .log import logger
from typing import Literal


def current_os() -> Literal["win", "posix"]:
    return 'win' if sep == '\\' else 'posix'


def assert_valid_style(style: str):
    if style not in ['win', 'posix']:
        logger.error("Unknown style, please specify 'win' or 'posix'.")
        raise ValueError("Unknown style, please specify 'win' or 'posix'.")


def relpath_to_style(path: str, style: Literal["win", "posix"]):
    assert_valid_style(style)
    if style == 'win' and '/' in path:
        path = path.replace('/', '\\')
    elif style == 'posix' and '\\' in path:
        path = path.replace('\\', '/')
    return path


def get_files_relpath(start_file: str, target_file_path: str, style: Literal["win", "posix"] = None):
    if not style:
        style = current_os()
    return relpath_to_style(relpath(target_file_path, dirname(start_file)), style)


def get_symlink_target_path(sym_file_location: str, target_style: Literal["win", "posix"] = None):
    if not target_style:
        target_style = current_os()
    target_path = readlink(sym_file_location)
    return relpath_to_style(normpath(join(dirname(sym_file_location), target_path)), target_style)


def symlink_to_style(sym_file_location: str, target_style: Literal["win", "posix"]):
    assert_valid_style(target_style)
    target_path = readlink(sym_file_location)
    if target_style == 'win' and '/' in target_path:
        target_path = target_path.replace('/', '\\')
    elif target_style == 'posix' and '\\' in target_path:
        target_path = target_path.replace('\\', '/')

    remove(sym_file_location)
    symlink(target_path, sym_file_location)


def recursive_change_symlink_style_in_dir(folder_path: str, target_style: Literal["win", "posix"]):
    assert_valid_style(target_style)
    for root, dirs, files in walk(folder_path):
        for file in files:
            sym_file_location = join(root, file)
            if islink(sym_file_location):
                symlink_to_style(sym_file_location, target_style)
