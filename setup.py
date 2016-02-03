from setuptools import setup
import re

with open('mxsampleship/__init__.py') as file:
    version = re.search(r"__version__ = '(.*)'", file.read()).group(1)

setup(
    name='mxsampleship',
    version=version,
    packages=['mxsampleship'],
    install_requires=[
        'Flask>=0.10.1',
        'Flask-Bootstrap>=3.3.5.7',
        'Flask-Login>=0.3.2',
        'Flask-QRcode>=0.6.0',
        'Flask-Script>=2.0.5',
        'Flask-WTF>=0.12',
        'portalapi>=0.2.3',
    ],
)
