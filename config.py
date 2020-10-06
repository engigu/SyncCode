import os


class Config:
    ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
    LOGS_PATH = os.path.join(ROOT_PATH, 'logs')


    HOST = '192.168.217.132'
    PORT = 22
    USERNAME = 'tk'
    PASSWORD = 'Aa123456'

    BASE_ROOT_PATH = '/home/tk/test666'

    FILTER_FILE_OR_DIRECTORY = ['.idea', '__pycache__', '.git']