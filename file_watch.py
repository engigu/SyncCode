#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'lihailin'
__mail__ = '415787837@qq.com'
__date__ = '2018-05-03'
__version__ = 1.0

import sys
import time
import traceback

import ftp
# 配置日志
import os
import logging
import log

log.initLogConf()
_logging = logging.getLogger(__file__)
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread

from sftp import SCPFile
from config import Config

# reload(sys)
# sys.setdefaultencoding('utf-8')

# 配置ftp
ip = 'vm.server'
username = 'tk'
passwd = 'Aa123456'

FILE_QUEUE = []
SEP = '|'


class Queue:
    def __init__(self):
        self._queue = FILE_QUEUE

    def get(self):
        if self._queue:
            return self._queue.pop(0)
        return None

    def put(self, item):
        if item not in self._queue:
            self._queue.append(item)


class ToServer(FileSystemEventHandler):
    '''
    将本地文件变化事件记录到日志中，并上传到服务器
    '''

    def __init__(self):
        super(ToServer, self).__init__()
        self.file_queue = Queue()
        # 配置ftp服务器
        # self.xfer = ftp.Xfer()
        # self.xfer.setFtpParams(ip, username, passwd)
        # # 开启服务时上传一遍文件至远程文件夹
        # self.xfer.upload(path)
        self.upload_hole_path('.')

    def upload_hole_path(self, path):
        # 上传整个文件夹
        for root, dirs, files in os.walk(path):
            for name in files:
                file = self.path_deal(os.path.join(root, name))
                if not self.need_filter_file_or_directory(file):
                    name = SEP.join([file, '', '', ''])
                    self.file_queue.put(name)

    def need_filter_file_or_directory(self, src_path):
        if any([f in src_path for f in Config.FILTER_FILE_OR_DIRECTORY]):
            return True
        return False

    def path_deal(self, path: str):
        return path.replace('\\', '/').replace('./', '')

    def on_any_event(self, event):
        # 将发生过的事件写入日志
        print('on_any_event:', event.event_type)
        print('on_any_event:', event.__dict__)

        name = SEP.join([
            self.path_deal(event.src_path),
            self.path_deal(event.dest_path) if hasattr(event, 'dest_path') else '',
            event.event_type,
            '1' if event.is_directory else '0'
        ])

        if not self.need_filter_file_or_directory(event.src_path):
            self.file_queue.put(name)

        if event.is_directory:
            is_d = 'directory'
        else:
            is_d = 'file'
        # log_s = "%s %s: %s " % (event.event_type, is_d, event.src_path)
        # print log_s
        # _logging.info(log_s)

    # def on_created(self, event):
    #     # 仅上传文件
    #     print(event.__dict__)
    #
    #     if event.is_directory:
    #         return
    #     # self.xfer.upload(event.src_path)
    #
    # def on_modified(self, event):
    #     print(event)
    #     print(event.__dict__)
    #     self.on_created(event)
    #
    # def on_deleted(self, event):
    #     print(event)
    #     print(event.__dict__)
    #
    # def on_moved(self, event):
    #     '''
    #     服务器中的文件进行移动
    #     '''
    #     print(event.__dict__)
    #
    #     # self.xfer.rename(event.src_path, event.dest_path)
    #     # log_s = "move file: %s to %s" % (event.src_path, event.dest_path)
    #     # _logging.info(log_s)
    #


class UploadToServer:
    def __init__(self):
        self.file_queue = Queue()
        self.logger = logging
        self.first = True
        pass

    def run(self):
        scp_client = SCPFile()

        while True:
            item = self.file_queue.get()
            if item is not None:
                print('item:::::', item)
                src_path, dest_path, action, is_directory = item.split(SEP)
                print(src_path, dest_path, action)
                try:
                    if action == 'moved':
                        scp_client.move_file(src_path, dest_path)
                        self.logger.info('move %r to %r' % (src_path, dest_path))
                    elif action == 'deleted':
                        scp_client.delete_file(src_path)
                    elif action in ['created', 'modified']:
                        scp_client.create_file(src_path)
                except:
                    print(traceback.format_exc())

            time.sleep(1)


def start_file_watcher():
    event_handler = ToServer()
    observer = Observer()
    observer.schedule(event_handler, '.', recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def start_upload_file():
    UploadToServer().run()


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Process config env')
    # parser.add_argument('-p', metavar='N', type=int, default=8080,
    #                     help='an integer for the accumulator')
    # parser.add_argument('-c', default="env", help='select the config env. default: local')
    # args = parser.parse_args()
    # port = args.p

    # event_handler = ToServer()
    # observer = Observer()
    # observer.schedule(event_handler, '.', recursive=True)
    # observer.start()
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     observer.stop()
    # observer.join()

    tasks = [
        Thread(target=start_file_watcher),
        Thread(target=start_upload_file)
    ]

    for task in tasks:
        task.start()
