#!/usr/bin/env python
import logging
from logging.config import dictConfig


def config_logging(logger):
    dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'timed': {
                'format': '%(levelname)s %(asctime)s %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
            'syslog': {
                'format': '%(name)s (%(process)d): %(levelname)s %(message)s'
            }
        },
        'handlers': {
            'null': {
                'class': 'logging.NullHandler'
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout',
            },
            'console-timed': {
                'class': 'logging.StreamHandler',
                'formatter': 'timed',
                'stream': 'ext://sys.stdout',
            },
            'file': {
                'class': 'logging.FileHandler',
                'formatter': 'simple',
                'filename': logger['FILE'],
            },
            'file-timed': {
                'class': 'logging.FileHandler',
                'formatter': 'timed',
                'filename': logger['FILE'],
            },
            'syslog': {
                'class': 'logging.handlers.SysLogHandler',
                'formatter': 'syslog',
            }
        },
        'loggers': {
            logger['NAME']: {
                'handlers': logger['HANDLERS'].split(','),
                'level': logger['LEVEL'],
                'propagate': True,
            }
        }
    })

    return logging.getLogger(logger['NAME'])