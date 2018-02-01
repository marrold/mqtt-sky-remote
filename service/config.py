#!/usr/bin/env python

import ConfigParser
from socket import gethostbyname
import sys


def build_config(_config_file):

    config = ConfigParser.ConfigParser()

    if not config.read(_config_file):
        sys.exit('Configuration file \'' + _config_file + '\' is not a valid. Exiting.')

    CONFIG = {}
    CONFIG['GLOBAL'] = {}
    CONFIG['MQTT'] = {}
    CONFIG['SKY_BOXES'] = {}

    try:
        for section in config.sections():

            if section == 'GLOBAL':
                CONFIG['GLOBAL'].update({
                    'FILE': config.get(section, 'FILE'),
                    'HANDLERS': config.get(section, 'HANDLERS'),
                    'LEVEL': config.get(section, 'LEVEL'),
                    'NAME': config.get(section, 'NAME'),
                    'LOG_TWISTED': config.getboolean(section, 'LOG_TWISTED')
                })

            elif section == 'MQTT':

                try:
                    username = config.get(section, 'USERNAME')
                except:
                    username = None

                try:
                    password = config.get(section, 'PASSWORD')
                except:
                    password = None

                CONFIG['MQTT'].update({
                    'HOST': config.get(section, 'HOST'),
                    'PORT': config.get(section, 'PORT'),
                    'USERNAME': username,
                    'PASSWORD': password,
                    'TLS': config.getboolean(section, 'TLS'),
                    'CERTS': config.get(section, 'CERTS'),
                })

            else:
                CONFIG['SKY_BOXES'].update({section: {
                    'HOST': gethostbyname(config.get(section, 'HOST')),
                    'SKY_Q': config.getboolean(section, 'SKY_Q')
                }})

    except ConfigParser.Error, err:
        print "Cannot parse configuration file. %s" % err
        sys.exit('Could not parse configuration file, exiting.')

    return CONFIG
