import os


class Config:
    ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
    LOGS_PATH = os.path.join(ROOT_PATH, 'logs')

    HOST = '192.168.217.132'
    PORT = 22
    USERNAME = 'tk'
    PASSWORD = 'Aa123456'

    FOLDER_MAPPING = {
        'E:\workspace\code\SyncCode': '/home/tk/test666/SyncCode',
        'E:\workspace\code\dockerServer': '/home/tk/test666/dockerServer',
    }

    FILTER_FILE_OR_DIRECTORY = [
        '.idea/*',
        '__pycache__/*',
        '.git/*',
        'logs/*'
    ]
