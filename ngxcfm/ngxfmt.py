# format nginx config folder.
import sys
from os import walk, readlink, remove, symlink
from os.path import exists, isfile, join, isabs, islink, isdir, relpath, dirname, basename
from pathlib import Path
from shutil import rmtree, move
from .log import logger
import posixpath as ix_path
from .os_symlink import relpath_to_style, current_os, get_files_relpath
from .switch_conf import get_available_conf_path, enable_nginx_conf

def format_nginx_conf_folder(conf_folder_path: str):
    import nginxfmt
    f = nginxfmt.Formatter()
    for root, dirs, files in walk(conf_folder_path):
        for file in files:
            file_path = join(root, file)
            if isfile(file_path) and not islink(file_path):
                logger.info(f'formatting {file_path}')
                f.format_file(Path(file_path))


# 对每个 *-enabled 中的文件都进行如下操作：
# 两个路径都必须是绝对路径
def check_and_try_to_fix_a_symlink_file(local_conf_file_path: str, local_conf_folder_path: str):
    if islink(local_conf_file_path):
        # 如果是符号链接，将指向的绝对路径转换成相对路径，并判断所指文件是否存在
        conf_file_target = readlink(local_conf_file_path)
        if ix_path.isabs(conf_file_target):
            logger.info(f'{local_conf_file_path} points to a abs location {conf_file_target}, try to fix it.')
            try:
                conf_file_target_normalized = ix_path.normpath(conf_file_target)
                local_conf_file_target = relpath_to_style(conf_file_target_normalized.replace('/etc/nginx', local_conf_folder_path), current_os())
                if exists(local_conf_file_target):
                    # 指向了一个存在的配置文件，更新符号链接所指为相对路径。
                    # relative_path = relpath(local_conf_file_target, dirname(local_conf_file_path))
                    relative_path = get_files_relpath(local_conf_file_path, local_conf_file_target)
                    remove(local_conf_file_path)
                    symlink(relative_path, local_conf_file_path)
                    logger.info(f'{local_conf_file_path} -> {relative_path}')
                else:
                    # 指向了不存在的配置文件，警告并删除符号链接。
                    logger.error(f'{local_conf_file_path} points to a non-existent location {conf_file_target}, remove it.')
                    remove(local_conf_file_path)
            except Exception as e:
                logger.error("error when trying to fix a symlink file: ", e)
        else:
            # 如果是相对路径，判断所指文件是否存在，注意在计算相对路径时源文件的文件名不应该被带上，否则会多出一级文件夹。
            local_conf_file_target = join(dirname(local_conf_file_path), conf_file_target)
            if not exists(local_conf_file_target):
                # 指向了不存在的配置文件，警告并删除符号链接。
                logger.error(f'{local_conf_file_path} points to a non-existent location {conf_file_target}, remove it.')
                remove(local_conf_file_path)
    elif isfile(local_conf_file_path):
        # 之前已经处理过 link 了， isfile 如果返回true不可能是link了，所以这里是普通文件。
        # *-enabled 下有一个普通文件，说明用户配置时取了巧，规范的行为应该是把这个普通文件移动到 ../*-available 下，然后再enable这个目标，注意查重。
        logger.warning(f'{local_conf_file_path} isn\'t a symlink file, moving...')
        available_conf_file_path = get_available_conf_path(local_conf_file_path)
        if exists(available_conf_file_path):
            # 如果 *-available 下已经有文件或内容，强制删除。
            logger.warning(f'{available_conf_file_path} already exists, remove it.')
            if isfile(available_conf_file_path):
                # 包括了 islink 的情况。
                remove(available_conf_file_path)
            elif isdir(available_conf_file_path):
                # 如果是文件夹，递归的删除所有内容。
                rmtree(available_conf_file_path)
        # 将普通文件移动到 *-available 下，变为规范的配置文件。
        move(local_conf_file_path, available_conf_file_path)
        # 启用这个配置文件。
        enable_nginx_conf(available_conf_file_path)
    else:
        # 什么？？？难道 *-enabled 下有一个目录？？？这太过分了，不可能修复，直接报错跳过。
        logger.error(f'{local_conf_file_path} is neither a symlink file nor a regular file, skip it.')
        return


def fix_nginx_conf_folder_symlink(local_conf_folder_path: str):
    # 重点检查 *-available 中的配置文件是否符合规范
    for root, dirs, files in walk(local_conf_folder_path):
        for file in files:
            conf_file_to_check = join(root, file)
            if basename(dirname(conf_file_to_check)).endswith('-enabled'):
                check_and_try_to_fix_a_symlink_file(conf_file_to_check, local_conf_folder_path)


if __name__ == '__main__':
    conf_folder_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not conf_folder_path:
        logger.error('no conf folder path specified')
        sys.exit(1)
    fix_nginx_conf_folder_symlink(conf_folder_path)
