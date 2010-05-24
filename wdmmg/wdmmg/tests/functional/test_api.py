from wdmmg.tests import *

import re

class TestApiController(TestController):
    @classmethod
    def setup_class(self):
        Fixtures.setup()
    
    @classmethod
    def teardown_class(self):
        Fixtures.teardown()

    # Many of tests have somewhat delicate assumptions about the exact
    # output of the JSON returned.  For example
    #     '"axes": []' in response
    # requires that there is no space between the key and the ":" and
    # exactly one space between the ":" and the value.  For clarities
    # sake, that's probably okay.  But could break.

    def test_index(self):
        response = unicode(self.app.get(url(controller='api', action='index')))
        assert '''the following requests:''' in response, response
        assert re.search(r'api/aggregate\?.*slice=', response), response
        assert re.search(r'api/aggregate\?.*exclude-', response), response
        assert re.search(r'api/aggregate\?.*include-', response), response
        assert re.search(r'api/aggregate\?.*breakdown-', response), response
        assert re.search(r'api/aggregate\?.*start_date=', response), response
        assert re.search(r'api/aggregate\?.*end_date=', response), response

    def test_aggregate(self):
        response = self.app.get(url(controller='api', action='aggregate',
            slice='cra'))
        assert '"metadata": {' in response, response
        assert '"slice": "cra"' in response, response
        assert '"exclude": []' in response, response
        assert '"include": []' in response, response
        assert '"dates": ["' in response, response
        assert '"axes": []' in response, response
        assert '"results": [[' in response

    def test_aggregate_with_breakdown(self):
        u = url(controller='api', action='aggregate', **{
            'slice': 'cra',
            'breakdown-region': 'yes',
        })
        print u
        response = self.app.get(u)
        assert '"axes": ["region"]' in response, response
        assert '"ENGLAND_London"' in response, response

    def test_aggregate_with_per(self):
        u = url(controller='api', action='aggregate', **{
            'slice': 'cra',
            'breakdown-region': 'yes',
            'per-population2006': 'region'
        })
        print u
        response = self.app.get(u)
        assert '"axes": ["region"]' in response, response
        assert '"ENGLAND_London"' in response, response
        assert '0.1' in response, response

    def test_aggregate_with_per_time(self):
        u = url(controller='api', action='aggregate', **{
            'slice': 'cra',
            'exclude-spender': 'yes',
            'per-gdp_deflator2006': ''
        })
        print u
        response = self.app.get(u)
        assert '"axes": []' in response, response
        assert '"2006-07"' in response, response
        assert '18445770.0' in response, response

    def test_mytax(self):
        u = url(controller='api', action='mytax', income=20000)
        print u
        response = self.app.get(u)
        assert '"tax": ' in response, response
        assert '"explanation": ' in response, response
