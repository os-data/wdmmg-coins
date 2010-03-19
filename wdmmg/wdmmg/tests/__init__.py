"""Pylons application test package

This package assumes the Pylons environment is already loaded, such as
when this script is imported from the `nosetests --with-pylons=test.ini`
command.

This module initializes the application via ``websetup`` (`paster
setup-app`) and provides the base testing objects.
"""
from unittest import TestCase

import pkg_resources
from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from pylons import config, url
from routes.util import URLGenerator
from webtest import TestApp

import pylons.test

import wdmmg.model as model
from wdmmg.getdata.cra import CRALoader

__all__ = ['environ', 'url', 'TestController', 'Fixtures']

# Invoke websetup with the current config file
SetupCommand('setup-app').run([config['__file__']])
# Does not work at the moment! (metadata not bound it seems)
# import wdmmg.model as model
# model.repo.rebuild_db()

environ = {}

class TestController(TestCase):

    def __init__(self, *args, **kwargs):
        if pylons.test.pylonsapp:
            wsgiapp = pylons.test.pylonsapp
        else:
            wsgiapp = loadapp('config:%s' % config['__file__'])
        self.app = TestApp(wsgiapp)
        url._push_object(URLGenerator(config['routes.map'], environ))
        TestCase.__init__(self, *args, **kwargs)

class Fixtures(object):
    @classmethod
    def setup(self):
        model.repo.delete_all()
        model.Session.remove()
        fileobj = pkg_resources.resource_stream('wdmmg', 'tests/cra_2009_db_short.csv')
        CRALoader.load(fileobj)
        model.Session.commit()
        model.Session.remove()
        self.slice_ = (model.Session.query(model.Slice)
            .filter_by(name=CRALoader.slice_name)
            ).one()
        self.govt_account = (model.Session.query(model.Account)
            .filter_by(name=CRALoader.govt_account_name)
            ).one()
        self.spender = model.Session.query(model.Key).filter_by(name=u'spender').one()
        self.dept = model.Session.query(model.Key).filter_by(name=u'dept').one()
        self.pog = model.Session.query(model.Key).filter_by(name=u'pog').one()
        self.cofog = model.Session.query(model.Key).filter_by(name=u'function').one()
        self.region = model.Session.query(model.Key).filter_by(name=u'region').one()
    
    @classmethod
    def teardown(self):
        model.repo.delete_all()
        model.Session.remove()

