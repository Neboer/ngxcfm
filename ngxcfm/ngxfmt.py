# format nginx config folder.
import sys
from os import walk, readlink, remove, symlink
from os.path import exists, isfile, join, isabs, islink, relpath, dirname, basename
from pathlib import Path
from .log import logger
import posixpath as ix_path
from .os_symlink import relpath_to_style, current_os, get_files_relpath


def format_nginx_conf_folder(conf_folder_path: str):
    import nginxfmt
    f = nginxfmt.Formatter()
    for root, dirs, files in walk(conf_folder_path):
        for file in files:
            if isfile(file):
                conf_file_to_format = join(root, file)
                logger.info(f'formatting {conf_file_to_format}')
                f.format_file(Path(conf_file_to_format))


# 对每个 sites-enabled 或 stream-enabled 中的文件都进行如下操作：
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
        # 如果是普通文件，查找
        logger.warning(f'{local_conf_file_path} is a file, not symlink!')


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
