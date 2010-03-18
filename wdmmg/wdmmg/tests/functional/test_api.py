from wdmmg.tests import *

import re

class TestApiController(TestController):
    @classmethod
    def setup_class(self):
        Fixtures.setup()
    
    @classmethod
    def teardown_class(self):
        Fixtures.teardown()

    def test_index(self):
        response = unicode(self.app.get(url(controller='api', action='index')))
        assert '''the following requests:''' in response, response
        print type(response)
        assert re.search(r'api/aggregate\?.*slice=', response), response
        assert re.search(r'api/aggregate\?.*spender_key=', response), response
        assert re.search(r'api/aggregate\?.*spender_value=', response), response
        assert re.search(r'api/aggregate\?.*breakdown_key1=', response), response
        assert re.search(r'api/aggregate\?.*start_date=', response), response
        assert re.search(r'api/aggregate\?.*end_date=', response), response

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

