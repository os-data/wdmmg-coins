from wdmmg.tests import *

class TestApiController(TestController):
    @classmethod
    def setup_class(self):
        Fixtures.setup()
    
    @classmethod
    def teardown_class(self):
        Fixtures.teardown()

    def test_index(self):
        response = self.app.get(url(controller='api', action='index'))
        assert '''the following URLs:''' in response
    
    def test_aggregate_help(self):
        response = self.app.get(url(controller='api', action='aggregate'))
        for p in [
            'slice', 'spender_key', 'spender_value', 'breakdown_key',
            'start_date', 'end_date'
        ]:
            assert p in response

    def test_aggregate(self):
        response = self.app.get(url(controller='api', action='aggregate',
            slice='cra'))
        assert '"metadata": {"axes": []}' in response
        assert '"results": [[' in response

    def test_aggregate_with_breakdown(self):
        response = self.app.get(url(controller='api', action='aggregate',
            slice='cra', breakdown_key1='region'))
        assert '"metadata": {"axes": ["region"]}' in response, response
        assert '"results": [[' in response, response
        assert '"ENGLAND_London"' in response, response

