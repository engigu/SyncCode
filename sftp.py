import os
from paramiko import SSHClient, Transport, AutoAddPolicy
from scp import SCPClient, SCPException

from config import Config
import logging


class SCPFile:
    src_base_path = ''
    dest_base_path = ''

    def __init__(self):
        self.ssh = self.ssh_client()
        self.logger = logging

    def ssh_client(self) -> SSHClient:
        tsp = SSHClient()
        tsp.set_missing_host_key_policy(AutoAddPolicy)
        tsp.connect(Config.HOST, Config.PORT, Config.USERNAME, Config.PASSWORD)
        return tsp

    def put(self, ssh, path, abs_path):
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(path, remote_path=abs_path, recursive=True)

    def create_file(self, path, do_logger=True):
        # ssh = self.ssh_client()
        ssh = self.ssh

        abs_path = self.remote_file_abs_path(path)
        dir_name = os.path.dirname(abs_path)
        ssh.exec_command('[ ! -d %s ] && mkdir -p %s' % (dir_name, dir_name))

        # with SCPClient(ssh.get_transport()) as scp:
        #     scp.put(path, remote_path=abs_path, recursive=True)

        self.put(ssh, path, abs_path)
        if do_logger:
            self.logger.info('upload %r to %r' % (path, abs_path))
        return path, abs_path

    def remote_file_abs_path(self, path):
        if os.path.isabs(path):
            commonpath = os.path.commonpath([self.src_base_path, path]).replace('\\', '/').replace('./', '')
            path = path.replace(commonpath, '').replace('\\', '/').replace('./', '')
            if path[:1] == '/':
                path = path[1:]
        abs_path = '/'.join([self.dest_base_path, path])
        return abs_path

    def delete_file(self, path, do_logger=True):
        abs_path = self.remote_file_abs_path(path)
        self.ssh.exec_command('rm %s -rf' % abs_path)

        if do_logger:
            self.logger.info('delete %r to %r' % (path, abs_path))

    def move_file(self, src_path, dest_path, do_logger=True):
        self.delete_file(src_path, do_logger=False)
        path, abs_path = self.create_file(dest_path, do_logger=False)
        if do_logger:
            self.logger.info('move %r to %r' % (src_path, abs_path))


if __name__ == '__main__':
    s = SCPFile()
    s.create_file('log.py')
