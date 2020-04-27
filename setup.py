#!/usr/bin/env python3
"""Setup file for websocket plots"""

from setuptools import setup, find_packages

with open('README.md') as f:
    README = f.read()

with open('LICENSE') as f:
    LICENSE = f.read()

setup(
    name="websocketplots",
    version='0.0.0',
    description="Plots served through websockets",
    long_description=README,
    author="Jooa Hooli",
    author_email="code@jooa.xyz",
    url="https://github.com/lysogeny/websocket-plots",
    license=LICENSE,
    packages=find_packages(exclude=('tests', 'docs')),
    entry_points={
        'console_scripts': [
            'wsp-server = websocketplots.entrypoints:server',
            'wsp-monitor = websocketplots.entrypoints:monitor',
            'wsp-random = websocketplots.entrypoints:random',
            'wsp-send = websocketplots.entrypoints:send'
        ]
    }
)
