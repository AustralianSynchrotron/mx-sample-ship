#!/usr/bin/env python

from flask.ext.script import Manager
from app import create_app
import os

app = create_app(os.environ.get('SAMPLE_SHIP_CONFIG', 'development'))
manager = Manager(app)


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    import pytest
    pytest.main([])


if __name__ == '__main__':
    manager.run()
