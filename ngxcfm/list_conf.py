# 列出当前所有的配置文件，并判断他们是否被启用，在终端里用不同颜色显示
# 默认所执行的配置文件夹已经规范化，不再做任何规范化检查。
from os import symlink, remove, makedirs, walk, listdir
from os.path import join, dirname, basename, exists, islink, relpath, isdir
from .log import logger
from .os_platform.os_checkdir import ensure_folders
from .switch_conf import get_enabled_conf_path
from typing import TypedDict
from colored import Fore, Back, Style


class ConfFile(TypedDict):
    file_name: str
    file_enabled: bool


def list_all_folders(parent_dir_path: str) -> list:
    return [x for x in listdir(parent_dir_path) if isdir(join(parent_dir_path, x))]

@ensure_folders(["conf_dir"])
def get_all_conf_files(conf_dir: str) -> dict[str, list[ConfFile]]:
    conf_files: dict[str, list[ConfFile]] = {}
    available_conf_dirs = [join(conf_dir, x) for x in list_all_folders(conf_dir) if x.endswith('-available')]
    for available_conf_dir in available_conf_dirs:
        dir_type = basename(available_conf_dir).replace('-available', '')
        conf_files[dir_type] = []
        for available_conf_filename in listdir(available_conf_dir):
            enabled_conf_file = get_enabled_conf_path(join(available_conf_dir, available_conf_filename))
            conf_files[dir_type].append({
                'file_name': available_conf_filename,
                'file_enabled': exists(enabled_conf_file)
            })
    return conf_files


def print_all_confs(conf_files: dict[str, list[ConfFile]]):
    for conf_type, conf_files in conf_files.items():
        print(f'{Style.BOLD}{conf_type}:{Style.reset}')  # 加粗打印
        sorted_conf_files = sorted(conf_files, key=lambda c: (not c['file_enabled'], c['file_name']))
        for conf_file in sorted_conf_files:
            if conf_file['file_enabled']:
                print(f'{Fore.GREEN}e:\t{conf_file["file_name"]}{Style.reset}')
            else:
                print(f'{Fore.RED}d:\t{conf_file["file_name"]}{Style.reset}')
        print()
