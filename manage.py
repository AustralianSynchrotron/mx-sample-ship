#!/usr/bin/env python

from flask.ext.script import Manager, Shell
from mxsampleship import create_app, mongo
import os


if __name__ == '__main__':

    app = create_app(os.environ.get('SAMPLE_SHIP_CONFIG', 'development'))
    manager = Manager(app)

    def make_shell_context():
        return dict(app=app, mongo=mongo)
    manager.add_command('shell', Shell(make_context=make_shell_context))

    manager.run()
