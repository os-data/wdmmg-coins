"""Pylons application test package

This package assumes the Pylons environment is already loaded, such as
when this script is imported from the `nosetests --with-pylons=test.ini`
command.

This module initializes the application via ``websetup`` (`paster
setup-app`) and provides the base testing objects.
"""
import shutil
import os

from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from pylons import config, url
from routes.util import URLGenerator
from webtest import TestApp

import pylons.test

__all__ = ['environ', 'url', 'TestController','clean_pairtree']

# Invoke websetup with the current config file
SetupCommand('setup-app').run([config['__file__']])

pairtree_dir = config['pairtree.args']
def clean_pairtree():
    if os.path.exists(pairtree_dir):
        shutil.rmtree(pairtree_dir)
clean_pairtree()

environ = {}

class TestController(object):

    def __init__(self, *args, **kwargs):
        if pylons.test.pylonsapp:
            wsgiapp = pylons.test.pylonsapp
        else:
            wsgiapp = loadapp('config:%s' % config['__file__'])
        self.app = TestApp(wsgiapp)
        url._push_object(URLGenerator(config['routes.map'], environ))

