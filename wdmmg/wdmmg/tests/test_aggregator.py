from datetime import date
import os, sys, csv
import pkg_resources

import wdmmg.model as model
import wdmmg.lib.aggregator as aggregator
from wdmmg.tests import Fixtures

class TestAggregator(object):
    @classmethod
    def setup_class(self):
        Fixtures.setup()
    
    @classmethod
    def teardown_class(self):
        Fixtures.teardown()
    
    def test_aggregator(self):
        ans = aggregator.aggregate(
            Fixtures.slice_,
            Fixtures.pog, spender_values=set([None]),
            breakdown_keys=[
                Fixtures.dept, Fixtures.cofog,
                # Omit Fixtures.pog, Fixtures.region,
            ])
        assert ans['metadata'] == {'axes': [u'dept', u'function']}, ans
        assert True or ans['results'] == [
            (608.89999999999998, (u'999', u'6. Housing and community amenities')),
            (-9.2000000000000011, (u'Dept004', u'of which: transport')),
            (-70.700000000000003, (u'Dept022', u'10. Social protection')),
            (-120.80000000000001, (u'Dept032', u'10. Social protection')),
            (-36.200000000000003, (u'Dept032', u'of which: employment policies')),
            (-0.5, (u'Dept047', u'3. Public order and safety')),
        ]
        return ans

