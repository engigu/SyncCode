import os
from paramiko import SSHClient, Transport, AutoAddPolicy
from scp import SCPClient

from config import Config
import logging


# ssh = SSHClient()
# ssh.load_system_host_keys()
# ssh.connect('example.com')
#
# with SCPClient(ssh.get_transport()) as scp:
#     scp.put('test.txt', 'test2.txt')
#     scp.get('test2.txt')


class SCPFile:

    def __init__(self):
        self.ssh = self.ssh_client()
        self.logger = logging
        pass

    def ssh_client(self) -> SSHClient:
        tsp = SSHClient()
        tsp.set_missing_host_key_policy(AutoAddPolicy)
        tsp.connect(Config.HOST, Config.PORT, Config.USERNAME, Config.PASSWORD)
        return tsp

    def put(self, ssh, path, abs_path):
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(path, remote_path=abs_path, recursive=True)

        # self.logger.info('upload %r to %r' % (path, abs_path))

    def create_file(self, path, do_logger=True):
        # ssh = self.ssh_client()
        ssh = self.ssh

        abs_path = self.remote_file_abs_path(path)
        dir_name = os.path.dirname(abs_path)
        ssh.exec_command('[ ! -d %s ] && mkdir -p %s' % (dir_name, dir_name))

        # with SCPClient(ssh.get_transport()) as scp:
        #     scp.put(path, remote_path=abs_path, recursive=True)

        self.put(ssh, path, abs_path)
        # ssh.close()
        if do_logger:
            self.logger.info('upload %r to %r' % (path, abs_path))

    def remote_file_abs_path(self, path):
        abs_path = '/'.join([Config.BASE_ROOT_PATH, path])
        return abs_path

    def delete_file(self, path, do_logger=True):
        abs_path = self.remote_file_abs_path(path)
        self.ssh.exec_command('rm %s -rf' % abs_path)

        if do_logger:
            self.logger.info('delete %r to %r' % (path, abs_path))

    def move_file(self, src_path, dest_path, do_logger=True):
        self.delete_file(src_path, do_logger=False)
        self.create_file(dest_path, do_logger=False)
        if do_logger:
            self.logger.info('move %r to %r' % (src_path, dest_path))

    def path_deal(self, path: str):
        return path.replace('\\', '/').replace('./', '')

    def upload_hole_path(self, path):
        # 上传整个文件夹
        for root, dirs, files in os.walk(path):
            for name in files:
                file = self.path_deal(os.path.join(root, name))
                self.create_file(file)


if __name__ == '__main__':
    s = SCPFile()
    s.create_file('log.py')
    s.upload_hole_path(
        ''
    )
    pass
