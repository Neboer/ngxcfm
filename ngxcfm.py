# 用法：ngxcfm [动作] [选项] [源] [目标]
# ngxcfm pull Server1 Server1NginxConfs
# ngxcfm push Server1NginxConfs Server1
# ngxcfm format Server1NginxConfs
# ngxcfm relink Server1NginxConfs
# ngxcfm enable Server1NginxConfs/sites-available/xxx.conf
# ngxcfm disable Server1NginxConfs/sites-available/xxx.conf

import argparse
import sys

from switch_conf import enable_nginx_conf, disable_nginx_conf
from transfer_nginx_files import download_server_nginx_conf_to_local_dir, upload_local_nginx_conf_to_server
from ngxfmt import format_nginx_conf_folder, fix_nginx_conf_folder_symlink

def main():
    parser = argparse.ArgumentParser(description='ngxcfm command-line tool')
    parser.add_argument('action', choices=['pull', 'push', 'format', 'relink', 'enable', 'disable'], help='Action to perform')
    parser.add_argument('source', help='Source for the action')
    parser.add_argument('target', nargs='?', help='Target for the action')
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
    else:
        print("Unknown action")
        sys.exit(1)

if __name__ == '__main__':
    main()
