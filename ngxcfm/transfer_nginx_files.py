from fabric import Connection
from tempfile import mkstemp
from os import makedirs, remove
from shutil import rmtree
from os.path import exists
from .log import logger
from .os_tar import unpack_posix_tar, pack_dense_posix_tar, PosixTarConfig


def download_server_nginx_conf_to_local_dir(server_name: str, local_dir: str):
    conn = Connection(server_name)
    try:
        conn.open()
    except Exception as e:
        logger.error(f'Failed to connect to {server_name}: {e}')
        return
    if exists(local_dir):
        logger.warning(f'{local_dir} already exists, overwriting...')
        rmtree(local_dir)
    makedirs(local_dir, exist_ok=True)
    conn.run('tar -cf /tmp/nginx-conf.tar -C /etc/nginx .')
    tmp_file = mkstemp()[1]
    conn.get('/tmp/nginx-conf.tar', tmp_file)
    conn.run('rm /tmp/nginx-conf.tar')
    unpack_posix_tar(tmp_file, local_dir)

# TODO: get_tar_config_from_server 需要从服务器获取配置
def get_tar_config_from_server(server_name: str) -> PosixTarConfig:
    return {
        'dir_mode': 0o755,
        'file_mode': 0o644,
        'owner_uid': 0,
        'owner_gid': 0
    }


def upload_local_nginx_conf_to_server(server_name: str, local_dir: str):
    conn = Connection(server_name)
    try:
        conn.open()
    except Exception as e:
        logger.error(f'Failed to connect to {server_name}: {e}')
        return

    def check_nginx_conf():
        return conn.run('nginx -t', warn=True)

    tmp_file = mkstemp()[1]
    pack_dense_posix_tar(local_dir, tmp_file, get_tar_config_from_server(server_name))
    conn.put(tmp_file, '/tmp/nginx-conf.tar')
    conn.run('rm -rf /etc/nginx.bak', warn=True)
    conn.run('mv /etc/nginx /etc/nginx.bak', warn=True)
    conn.run('mkdir -p /etc/nginx')
    conn.run('tar -xf /tmp/nginx-conf.tar -C /etc/nginx')
    if check_nginx_conf().failed:
        logger.error('new conf test failed, rolling back')
        conn.run('rm -rf /etc/nginx')
        conn.run('mv /etc/nginx.bak /etc/nginx')
    conn.run('rm /tmp/nginx-conf.tar', warn=True)
    conn.run('nginx -s reload')

