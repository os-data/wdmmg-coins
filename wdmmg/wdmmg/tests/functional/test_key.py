from wdmmg.tests import *

class TestKeyController(TestController):

    @classmethod
    def setup_class(self):
        Fixtures.setup()
    
    @classmethod
    def teardown_class(self):
        Fixtures.teardown()

    def test_view(self):
        response = self.app.get(url(controller='key', action='view', id_=Fixtures.region.id))
        assert '''region''' in response
        assert '''ENGLAND_London''' in response
    
    def test_view_paginate(self):
        response = self.app.get(url(controller='key', action='view', id_=Fixtures.pog.id, items_per_page=3))
        assert '''Next''' in response

