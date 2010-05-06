from wdmmg.tests import *

import re

class TestAggregateController(TestController):
    @classmethod
    def setup_class(self):
        Fixtures.setup()
    
    @classmethod
    def teardown_class(self):
        Fixtures.teardown()

    def test_view(self):
        response = self.app.get(url(controller='aggregate', action='view'))
        assert "Spending" in response, response
        assert "2003-04" in response, response
        assert "2010-11" in response, response

    def test_view_with_breakdown(self):
        response = self.app.get(url(controller='aggregate', action='view', **{
            'breakdown': 'region',
        }))
        assert "Only show spending where:" not in response, response
        assert "Total" in response, response

    def test_view_with_filter(self):
        response = self.app.get(url(controller='aggregate', action='view', **{
            'include-cofog1': '10'
        }))
        assert "Only show spending where:" in response, response
        assert "Key 'cofog1' has value '10'." in response, response
        assert "Total" not in response, response

    def test_view_links(self):
        response = self.app.get(url(controller='aggregate', action='view', **{
            'breakdown': 'region',
            'include-cofog1': '10'
        }))
        # Check form submission will preserve filter.
        assert '<form action="/aggregate" method="get">' in response, response
        assert '<input type="hidden" name="include-cofog1" value="10" />' in response, response
        # Check 'remove' link will preserve breakdown.
        assert '<a href="/aggregate?breakdown=region">' in response, response
        # Check 'add' link will preserve filter and breakdown.
        assert '<a href="/aggregate?include-cofog1=10&amp;include-region=ENGLAND_West+Midlands">' in response, response

