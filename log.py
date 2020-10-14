# coding=utf-8
import os
import datetime
import logging
import logging.config


def genLogDict(logDir, logFile):
    '''
    配置日志格式的字典
    '''
    logDict = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                'format': '[%(levelname).1s %(asctime)s %(filename)s:%(lineno)d] - %(message)s'
            },
            'standard': {
                'format': '[%(levelname).1s %(asctime)s %(filename)s:%(lineno)d] - %(message)s'
            },
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",
            },
            "default": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "simple",
                "filename": os.path.join(logDir, logFile),
                'mode': 'w+',
                "maxBytes": 1024 * 1024 * 5,  # 5 MB
                "backupCount": 20,
                "encoding": "utf8"
            },
        },

        "root": {
            'handlers': ['default', 'console'],
            'level': "INFO",
            'propagate': False
        }
    }
    return logDict


def initLogConf():
    """
    配置日志
    """
    baseDir = os.path.dirname(os.path.abspath(__file__))
    logDir = os.path.join(baseDir, "logs")
    if not os.path.exists(logDir):
        os.makedirs(logDir)  # 创建路径

    logFile = datetime.datetime.now().strftime("%Y-%m-%d") + ".log"
    logDict = genLogDict(logDir, logFile)
    logging.config.dictConfig(logDict)


if __name__ == '__main__':
    initLogConf()
    log = logging.getLogger(__file__)
    log.info("log B")
