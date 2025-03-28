import sys
from os import symlink, remove, makedirs
from os.path import join, dirname, basename, exists, islink
from .log import logger
from .os_platform.os_symlink import get_files_relpath

# 给定一个 *-enabled 的目标，返回对应的 *-available 目标。
def get_available_conf_path(enabled_conf_file_path: str):
    enabled_dir = dirname(enabled_conf_file_path)
    if not enabled_dir.endswith('-enabled'):
        logger.error(f"Configuration file {enabled_conf_file_path} is not in the '-enabled' directory.")
        return
    available_dir = enabled_dir.replace('-enabled', '-available')
    enabled_file_name = basename(enabled_conf_file_path)
    available_file_path = join(available_dir, enabled_file_name)
    return available_file_path

# 反过来，给定一个 *-available 的目标，返回对应的 *-enabled 目标。
def get_enabled_conf_path(available_conf_file_path: str):
    available_dir = dirname(available_conf_file_path)
    if not available_dir.endswith('-available'):
        logger.error(f"Configuration file {available_conf_file_path} is not in the '-available' directory.")
        return
    enabled_dir = available_dir.replace('-available', '-enabled')
    available_file_name = basename(available_conf_file_path)
    enabled_file_path = join(enabled_dir, available_file_name)
    return enabled_file_path


def manage_nginx_conf(conf_file_path: str, action: str):
    enabled_file_path = get_enabled_conf_path(conf_file_path)
    enabled_dir = dirname(enabled_file_path)

    if action == 'enable':
        if not exists(conf_file_path):
            logger.error(f"Configuration file {conf_file_path} does not exist.")
            return

        makedirs(enabled_dir, exist_ok=True)
        if islink(enabled_file_path):
            logger.warning(f"Symlink {enabled_file_path} already exists, replace it.")
            remove(enabled_file_path)

        relative_path = get_files_relpath(enabled_file_path, conf_file_path)
        symlink(relative_path, enabled_file_path)
        logger.info(f"Enabled {conf_file_path} by creating symlink {enabled_file_path} -> {relative_path}")

    elif action == 'disable':
        if not exists(enabled_file_path):
            logger.error(f"Symbolic link {enabled_file_path} does not exist.")
            return

        if not islink(enabled_file_path):
            logger.error(f"{enabled_file_path} is not a symbolic link.")
            return

        remove(enabled_file_path)
        logger.info(f"Disabled {conf_file_path} by removing symlink {enabled_file_path}")

def enable_nginx_conf(conf_file_path: str):
    manage_nginx_conf(conf_file_path, 'enable')

def disable_nginx_conf(conf_file_path: str):
    manage_nginx_conf(conf_file_path, 'disable')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        logger.error("Usage: python script.py <enable|disable> <nginx_conf_file_path>")
        sys.exit(1)

    action = sys.argv[1]
    conf_file_path = sys.argv[2]

    if action == 'enable':
        enable_nginx_conf(conf_file_path)
    elif action == 'disable':
        disable_nginx_conf(conf_file_path)
    else:
        logger.error("Unknown action. Use 'enable' or 'disable'.")
        sys.exit(1)
