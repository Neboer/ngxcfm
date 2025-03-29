# symlink 在Windows中的作用非常奇怪，这个函数的作用旨在规范这个问题。
from os import walk, readlink, remove, symlink
from os.path import join, islink, relpath, dirname, normpath
from typing import Literal
from ._os_style import current_os, assert_valid_style, optional_style_default_current_os
from .os_checkdir import ensure_folders


@optional_style_default_current_os
def relpath_to_style(path: str, style: Literal["win", "posix"] = None):
    if style == 'win' and '/' in path:
        path = path.replace('/', '\\')
    elif style == 'posix' and '\\' in path:
        path = path.replace('\\', '/')
    return path

@optional_style_default_current_os
def get_files_relpath(start_file: str, target_file_path: str, style: Literal["win", "posix"] = None):
    return relpath_to_style(relpath(target_file_path, dirname(start_file)), style)

@optional_style_default_current_os
def get_symlink_target_path(sym_file_location: str, style: Literal["win", "posix"] = None):
    target_path = readlink(sym_file_location)
    return relpath_to_style(normpath(join(dirname(sym_file_location), target_path)), style)

@optional_style_default_current_os
def symlink_to_style(sym_file_location: str, style: Literal["win", "posix"] = None):
    target_path = readlink(sym_file_location)
    if style == 'win' and '/' in target_path:
        target_path = target_path.replace('/', '\\')
    elif style == 'posix' and '\\' in target_path:
        target_path = target_path.replace('\\', '/')

    remove(sym_file_location)
    symlink(target_path, sym_file_location)

@ensure_folders(["folder_path"])
@optional_style_default_current_os
def recursive_convert_symlink_style_in_dir(folder_path: str, style: Literal["win", "posix"] = None):
    for root, dirs, files in walk(folder_path):
        for file in files:
            sym_file_location = join(root, file)
            if islink(sym_file_location):
                symlink_to_style(sym_file_location, style)

