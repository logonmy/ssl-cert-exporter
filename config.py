#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from util import util
from tomlkit import document, dumps, loads
logger = logging.getLogger(__name__)


class Config:
    #load config file
    def __init__(self):
        file_path = 'config.toml'
        util.ensure_file_exists(file_path)
        self.general = dict()
        self.domains = dict()
        with open(file_path) as c_file:
            config = loads(c_file.read())
        try:
            self.general = config['general']
        except Exception as e:
            logger.warning('toml: %s, [general] content is empty...' % file_path)
            pass
        try:
            self.domains = config['domains']
        except Exception as e:
            logger.warning('toml: %s, [domains] content is empty...' % file_path)
            pass

