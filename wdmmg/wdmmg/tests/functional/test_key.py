from wdmmg.tests import *

class TestKeyController(TestController):

    @classmethod
    def setup_class(self):
        Fixtures.setup()
    
    @classmethod
    def teardown_class(self):
        Fixtures.teardown()

    def test_index(self):
        response = self.app.get(url(controller='key', action='index'))
        assert '''The database contains the following keys:''' in response
        assert '''spender''' in response

    def test_view(self):
        response = self.app.get(url(controller='key', action='view', name_or_id=Fixtures.region.name))
        assert '''region''' in response
        assert '''ENGLAND_London''' in response
    
    def test_view_paginate(self):
        response = self.app.get(url(controller='key', action='view', name_or_id=Fixtures.pog.name, items_per_page=3))
        assert '''Next''' in response

    def test_accounts(self):
        response = self.app.get(url(controller='key', action='accounts', name_or_id=Fixtures.spender.name))
        assert Fixtures.spender.name in response
        assert Fixtures.govt_account.name in response

