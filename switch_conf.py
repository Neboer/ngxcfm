import sys
from os import symlink, remove, makedirs
from os.path import join, dirname, basename, exists, islink, relpath
from log import logger
from os_symlink import relpath_to_style, current_os, get_files_relpath


def enable_nginx_conf(conf_file_path: str):
    conf_dir = dirname(conf_file_path)
    conf_file_name = basename(conf_file_path)
    enabled_dir = conf_dir.replace('-available', '-enabled')
    symlink_path = join(enabled_dir, conf_file_name)

    if not exists(conf_file_path):
        logger.error(f"Configuration file {conf_file_path} does not exist.")
        return

    makedirs(enabled_dir, exist_ok=True)
    if islink(symlink_path):
        logger.warning(f"Symlink {symlink_path} already exists, replace it.")
        remove(symlink_path)

    relative_path = get_files_relpath(conf_file_path, symlink_path)
    symlink(relative_path, symlink_path)
    logger.info(f"Enabled {conf_file_path} by creating symlink {symlink_path} -> {relative_path}")


def disable_nginx_conf(conf_file_path: str):
    conf_dir = dirname(conf_file_path)
    conf_file_name = basename(conf_file_path)
    enabled_dir = conf_dir.replace('-available', '-enabled')
    symlink_path = join(enabled_dir, conf_file_name)

    if not exists(symlink_path):
        logger.error(f"Symbolic link {symlink_path} does not exist.")
        return

    if not islink(symlink_path):
        logger.error(f"{symlink_path} is not a symbolic link.")
        return

    remove(symlink_path)
    logger.info(f"Disabled {conf_file_path} by removing symlink {symlink_path}")


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
