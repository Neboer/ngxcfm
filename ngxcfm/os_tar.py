from tarfile import TarFile, TarInfo
from typing import Literal, TypedDict

from .os_symlink import relpath_to_style, current_os
import posixpath as ix_path
from os.path import isdir, isfile, join, split, splitext, isabs
from .log import logger


class PosixTarConfig(TypedDict):
    dir_mode: int
    file_mode: int
    owner_uid: int
    owner_gid: int


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

        elif tarinfo.isfile():
            tarinfo.mode = tar_config['file_mode']  # rw-r--r--
        elif tarinfo.isdir():
            tarinfo.mode = tar_config["dir_mode"]  # rwxr-xr-x
        tarinfo.uid = tar_config["owner_uid"]
        tarinfo.gid = tar_config["owner_gid"]

        return tarinfo

    return _pack_posix_tar_filter


def unpack_posix_tar(tar_file_path: str, target_dir: str):
    tar_file = TarFile.open(tar_file_path)
    tar_file.extractall(target_dir, filter=_unpack_posix_tar_filter)
    tar_file.close()


# 将一个文件夹打包成tar文件，文件夹本身就是tar文件的最高层。
def pack_dense_posix_tar(source_dir: str, tar_file_path: str, tar_config: PosixTarConfig):
    tar_file = TarFile.open(tar_file_path, 'w')
    tar_file.add(source_dir, filter=generate_pack_posix_tar_filter(tar_config), arcname=".")
    tar_file.close()
