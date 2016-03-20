#!/usr/bin/env python

from flask.ext.script import Manager
from mxsampleship import create_app
import os


if __name__ == '__main__':

    app = create_app(os.environ.get('SAMPLE_SHIP_CONFIG', 'development'))
    manager = Manager(app)

    manager.run()
