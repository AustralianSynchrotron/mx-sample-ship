#!/usr/bin/env python

from flask.ext.script import Manager, Shell
from app import create_app, mongo
import os

app = create_app(os.environ.get('SAMPLE_SHIP_CONFIG', 'development'))
manager = Manager(app)

def make_shell_context():
    return dict(app=app, mongo=mongo)
manager.add_command('shell', Shell(make_context=make_shell_context))


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    import pytest
    pytest.main(['-s'])


if __name__ == '__main__':
    manager.run()
