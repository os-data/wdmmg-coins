from wdmmg.tests import *

import wdmmg.model as model

class TestTransactionController(TestController):
    @classmethod
    def setup_class(self):
        Fixtures.setup()
    
    @classmethod
    def teardown_class(self):
        Fixtures.teardown()

    def test_index(self):
        response = self.app.get(url(controller='transaction', action='index'))
        assert '36 transactions' in response, response
        # name of an account
        assert 'Government (Dummy)' in response, response

    def test_view(self):
        t = model.Session.query(model.Transaction).first()
        response = self.app.get(url(controller='transaction', action='view', id_=t.id))
        assert '''cra''' in response
        assert Fixtures.govt_account.name in response

