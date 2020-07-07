#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

def ensure_file_exists(path):
    """ Create file if it doesn't exist
    :param path: path of file to create
    :type path: str
    :rtype: None
    """
    if not os.path.exists(path):
        try:
            open(path,'w').close()
            os.chmod(path,0o600)
        except IOError as e:
            raise Exception(
                'Cannot create file [{}]: {}'.format(path, e)
            )
