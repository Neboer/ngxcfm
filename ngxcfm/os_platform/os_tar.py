from tarfile import TarFile, TarInfo
from typing import Literal, TypedDict

from .os_checkdir import ensure_folders
from .os_symlink import relpath_to_style
from ._os_style import current_os
import posixpath as ix_path
from os.path import isdir, isfile, join, split, splitext, isabs
from ..log import logger
from tempfile import mkdtemp
from shutil import move, copytree, rmtree
from .os_file import recursive_convert_line_endings_style_in_dir


class PosixTarConfig(TypedDict):
    dir_mode: int
    file_mode: int
    owner_uid: int
    owner_gid: int


default_tar_config = {
    'dir_mode': 0o755,
    'file_mode': 0o644,
    'owner_uid': 0,
    'owner_gid': 0
}


def _unpack_posix_tar_filter(tarinfo: TarInfo, _: str) -> TarInfo:
    if tarinfo.issym():
        if not ix_path.isabs(tarinfo.linkname):
            new_link_name = relpath_to_style(tarinfo.linkname, current_os())
            logger.info(f"Fixing symlink {tarinfo.linkname} to {new_link_name}")
            tarinfo.linkname = new_link_name
        else:
            # 错误！tar文件中包括指向绝对路径的符号链接，这是绝对错误的，需要修复。
            logger.error(f"Unexpected absolute symlink {tarinfo.path} -> {tarinfo.linkname}")
    return tarinfo


def generate_pack_posix_tar_filter(tar_config: PosixTarConfig):
    def _pack_posix_tar_filter(tarinfo: TarInfo) -> TarInfo:
        if tarinfo.issym() and not isabs(tarinfo.linkname):
            new_link_name = relpath_to_style(tarinfo.linkname, "posix")
            logger.info(f"Fixing symlink {tarinfo.linkname} to {new_link_name}")
            tarinfo.linkname = new_link_name

        if tarinfo.issym():
            tarinfo.mode = 0o777  # rwxrwxrwx
        elif tarinfo.isfile():
            tarinfo.mode = tar_config['file_mode']  # rw-r--r--
        elif tarinfo.isdir():
            tarinfo.mode = tar_config["dir_mode"]  # rwxr-xr-x

        tarinfo.uid = tar_config["owner_uid"]
        tarinfo.gid = tar_config["owner_gid"]

        return tarinfo

    return _pack_posix_tar_filter


# 在当前平台上解压tar文件，注意这里的解压是将文件夹本身作为tar文件的最高层。
def unpack_posix_tar(tar_file_path: str, target_dir: str):
    tar_file = TarFile.open(tar_file_path)
    tar_file.extractall(target_dir, filter=_unpack_posix_tar_filter)
    tar_file.close()
    recursive_convert_line_endings_style_in_dir(target_dir)


# 将一个文件夹拷贝到临时文件夹，执行recursive_change_line_endings_style_in_dir，然后打包成tar文件。
@ensure_folders(["source_dir"])
def pack_dense_posix_tar(source_dir: str, tar_file_path: str, tar_config=None):
    if tar_config is None:
        tar_config = default_tar_config
    temp_dir = mkdtemp()
    rmtree(temp_dir, ignore_errors=True)
    copytree(source_dir, temp_dir, symlinks=True, ignore_dangling_symlinks=True)
    recursive_convert_line_endings_style_in_dir(temp_dir, "posix")
    tar_file = TarFile.open(tar_file_path, 'w')
    tar_file.add(temp_dir, filter=generate_pack_posix_tar_filter(tar_config), arcname=".")
    tar_file.close()
    rmtree(temp_dir)
