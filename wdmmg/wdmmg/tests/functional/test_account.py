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

    def test_postings(self):
        response = self.app.get(url(controller='account', action='postings',
            id_=Fixtures.govt_account.id, items_per_page=3))
        assert '''The following postings have been made against account''' in response
        assert Fixtures.govt_account.name in response
        assert '''Next''' in response

