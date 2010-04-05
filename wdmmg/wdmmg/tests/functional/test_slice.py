from wdmmg.tests import *

class TestSliceController(TestController):

    @classmethod
    def setup_class(self):
        Fixtures.setup()
    
    @classmethod
    def teardown_class(self):
        Fixtures.teardown()

    def test_index(self):
        response = self.app.get(url(controller='slice', action='index'))
        assert '''The database contains the following slices:''' in response
        assert 'cra' in response

    def test_view(self):
        response = self.app.get(url(controller='slice', action='view', id_or_name='cra'))
        assert '''Properties of slice 'cra':''' in response
        assert '''Number of accounts:''' in response
        assert '''Number of transactions:''' in response

    def test_accounts(self):
        response = self.app.get(url(controller='slice', action='accounts', id_or_name='cra'))
        assert "'cra'" in response
        assert '''contains the following accounts:''' in response
        assert Fixtures.govt_account.name in response


