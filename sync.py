#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import traceback
import os

import fnmatch
import logging
import log

log.initLogConf()
_logging = logging.getLogger(__file__)
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread

from sftp import SCPFile, SCPException
from config import Config

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

    def __init__(self, src_base_path, dest_base_path):
        super(ToServer, self).__init__()
        self.file_queue = Queue()
        self.src_base_path = src_base_path
        self.dest_base_path =dest_base_path
        # # 开启服务时上传一遍文件至远程文件夹
        self.upload_hole_path()
        logging.info('ready to upload files...')

    def upload_hole_path(self):
        # 上传整个文件夹
        path = self.src_base_path
        for root, dirs, files in os.walk(path):
            for name in files:
                file = self.path_deal(os.path.join(root, name))
                if not self.need_filter_file_or_directory(file):
                    name = SEP.join([file, '', 'mutil', self.src_base_path, self.dest_base_path, ''])
                    self.file_queue.put(name)

    def need_filter_file_or_directory(self, src_path):
        if os.path.isabs(src_path):
            commonpath = self.path_deal(os.path.commonpath([self.src_base_path, src_path]))
            path = self.path_deal(src_path.replace(commonpath, ''))
            if path[:1] == '/':
                src_path = path[1:]
        else:
            src_path = self.path_deal(src_path)

        if any([fnmatch.fnmatchcase(src_path, pat=f) for f in Config.FILTER_FILE_OR_DIRECTORY if f]):
            return True
        return False

    def path_deal(self, path: str):
        return path.replace('\\', '/').replace('./', '')

    def on_any_event(self, event):
        # 将发生过的事件写入日志

        name = SEP.join([
            self.path_deal(event.src_path),
            self.path_deal(event.dest_path) if hasattr(event, 'dest_path') else '',
            event.event_type,
            self.src_base_path,
            self.dest_base_path,
            '1' if event.is_directory else '0'
        ])

        if not self.need_filter_file_or_directory(self.path_deal(event.src_path)):
            self.file_queue.put(name)


class UploadToServer:
    def __init__(self):
        self.file_queue = Queue()
        self.logger = logging
        self.first = True

    def run(self):
        scp_client = SCPFile()

        while True:
            item = self.file_queue.get()
            if item is not None:
                src_path, dest_path, action, src_base_path, dest_base_path, is_directory = item.split(SEP)
                setattr(scp_client, 'src_base_path', src_base_path)
                setattr(scp_client, 'dest_base_path', dest_base_path)
                # print('item', item)
                try:
                    if action == 'moved':
                        scp_client.move_file(src_path, dest_path)
                        self.logger.info('move %r to %r' % (src_path, dest_path))
                    elif action == 'deleted':
                        scp_client.delete_file(src_path)
                    elif action in ['created', 'modified']:
                        scp_client.create_file(src_path)
                    elif action == 'mutil':
                        # no sleep
                        scp_client.create_file(src_path)
                        continue

                except FileNotFoundError:
                    pass
                # except SCPException:
                #     pass
                except KeyboardInterrupt:
                    break
                except:
                    print(traceback.format_exc())

            time.sleep(0.1)


def start_file_watcher():
    observer = Observer()
    for src_path, dest_path in Config.FOLDER_MAPPING.items():
        event_handler = ToServer(src_path, dest_path)
        observer.schedule(event_handler, src_path, recursive=True)
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
    tasks = [
        Thread(target=start_file_watcher),
        Thread(target=start_upload_file)
    ]

    for task in tasks:
        task.setDaemon(True)
        task.start()

    for task in tasks:
        task.join()
