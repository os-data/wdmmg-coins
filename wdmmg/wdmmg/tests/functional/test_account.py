from wdmmg.tests import *

class TestAccountController(TestController):

    @classmethod
    def setup_class(self):
        Fixtures.setup()
    
    @classmethod
    def teardown_class(self):
        Fixtures.teardown()

    def test_view(self):
        response = self.app.get(url(controller='account', action='view', id_=Fixtures.govt_account.id))
        assert '''cra''' in response
        assert Fixtures.govt_account.name in response
        assert Fixtures.spender.name in response

