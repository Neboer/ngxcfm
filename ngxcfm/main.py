# 用法：ngxcfm [动作] [选项] [源] [目标]
# ngxcfm pull Server1 Server1NginxConfs
# ngxcfm push Server1NginxConfs Server1
# ngxcfm format Server1NginxConfs
# ngxcfm relink Server1NginxConfs
# ngxcfm enable Server1NginxConfs/sites-available/xxx.conf
# ngxcfm disable Server1NginxConfs/sites-available/xxx.conf

import argparse
import sys

from .list_conf import get_all_conf_files, print_all_confs
from .os_platform.os_symlink import recursive_convert_symlink_style_in_dir
from .os_platform.os_file import recursive_convert_line_endings_style_in_dir
from .os_platform.os_tar import pack_dense_posix_tar, unpack_posix_tar
from .switch_conf import enable_nginx_conf, disable_nginx_conf
from .transfer_nginx_files import download_server_nginx_conf_to_local_dir, upload_local_nginx_conf_to_server
from .ngxfmt import format_nginx_conf_folder, fix_nginx_conf_folder_symlink
from ngxcfm import __version__

def ngxcfm_main():
    parser = argparse.ArgumentParser(description='ngxcfm command-line tool')
    parser.add_argument('action', choices=['pull', 'push', 'format', 'relink', 'enable', 'disable', 'list', 'to-unix', 'to-win', 'tar', 'untar'], help='Action to perform')
    parser.add_argument('source', help='Source for the action')
    parser.add_argument('target', nargs='?', help='Target for the action')
    parser.add_argument('--version', action='version', version=f'ngxcfm {__version__}')
    args = parser.parse_args()

    if args.action == 'pull':
        if not args.target:
            print("Target directory is required for pull action")
            sys.exit(1)
        download_server_nginx_conf_to_local_dir(args.source, args.target)
    elif args.action == 'push':
        if not args.target:
            print("Target server is required for push action")
            sys.exit(1)
        upload_local_nginx_conf_to_server(args.target, args.source)
    elif args.action == 'format':
        format_nginx_conf_folder(args.source)
    elif args.action == 'relink':
        fix_nginx_conf_folder_symlink(args.source)
    elif args.action == 'enable':
        enable_nginx_conf(args.source)
    elif args.action == 'disable':
        disable_nginx_conf(args.source)
    elif args.action == 'list':
        print_all_confs(get_all_conf_files(args.source))
    elif args.action == 'to-unix':
        recursive_convert_symlink_style_in_dir(args.source, 'posix')
        recursive_convert_line_endings_style_in_dir(args.source, 'posix')
    elif args.action == 'to-win':
        recursive_convert_symlink_style_in_dir(args.source, 'win')
        recursive_convert_line_endings_style_in_dir(args.source, 'win')
    elif args.action == 'tar':
        pack_dense_posix_tar(args.source, args.target)
    elif args.action == 'untar':
        unpack_posix_tar(args.source, args.target)
    else:
        print("Unknown action")
        sys.exit(1)

if __name__ == '__main__':
    ngxcfm_main()
