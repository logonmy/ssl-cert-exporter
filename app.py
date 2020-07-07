#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
from flask import Flask
from typing import Dict, Generator
import textwrap
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from wsgiref.simple_server import make_server
import time
from ssl_cert_monitor import ExportToPrometheus,ExpiryData
from prometheus_client.core import REGISTRY

import os ,sys
from sys import  exit

sys.path.append(os.path.dirname(__file__))

ex_cls = ExpiryData()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app_dispatch = DispatcherMiddleware(app, {
        '/metrics': make_wsgi_app()
    })
    return app_dispatch


def parse_args() -> Dict:
    parser = argparse.ArgumentParser(
        description='statistics exporter for prometheus.io',
        allow_abbrev=False,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        '-p', '--port',
        metavar='<port>',
        type=int,
        required=False,
        default=ex_cls.port,
        help=textwrap.dedent('''\
            The port the exporter listens on for Prometheus queries.
            Default: 8800'''))

    args = parser.parse_args()
    return vars(args)


def main():
    args = parse_args()
    REGISTRY.register(ExportToPrometheus())
    app = create_app()
    httpd = make_server('', args['port'], app)
    httpd.serve_forever()
    print('Starting exporter...')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Exiting...')
        exit(0)


if __name__ == "__main__":
    main()
