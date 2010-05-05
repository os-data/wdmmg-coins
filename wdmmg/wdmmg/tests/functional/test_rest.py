from wdmmg.tests import *
import wdmmg.model as model

class TestRestController(TestController):
    @classmethod
    def setup_class(self):
        Fixtures.setup()
    
    @classmethod
    def teardown_class(self):
        Fixtures.teardown()
    
    def test_index(self):
        response = self.app.get(url(controller='rest', action='index'))
        for word in ['slice', 'account', 'transaction', 'key', 'enumeration_value']:
            assert word in response, response
    
    def test_slice(self):
        response = self.app.get(url(controller='rest', action='slice',
            name_or_id=Fixtures.slice_.name))
        assert '"id":' in response, response
        assert '"name": "cra"' in response, response
    
    def test_account(self):
        response = self.app.get(url(controller='rest', action='account',
            id_=Fixtures.govt_account.id))
        assert '"id":' in response, response
        assert '"spender": "yes"' in response, response
    
    def test_transaction(self):
        example = (model.Session.query(model.Transaction)
            .filter_by(slice_=Fixtures.slice_)
            ).first()
        response = self.app.get(url(controller='rest', action='transaction',
            id_=example.id))
        assert '"id":' in response, response
        assert '"postings":' in response, response
        assert '"spender": "yes"' in response, response

    def test_key(self):
        response = self.app.get(url(controller='rest', action='key',
            name_or_id=Fixtures.cofog2.name))
        assert '"id":' in response, response
        assert '"enumeration_values":' in response, response
        assert '"04.5":' in response, response
        assert '"parent":' in response, response

    def test_enumeration_value(self):
        example = (model.Session.query(model.EnumerationValue)
            .filter_by(key=Fixtures.region)
            ).first()
        response = self.app.get(url(controller='rest', action='enumeration_value',
            id_=example.id))
        assert '"id":' in response, response
        assert '"code":' in response, response
        assert '"population2006":' in response, response

