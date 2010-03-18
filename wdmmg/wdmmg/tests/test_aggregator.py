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
    
    def test_aggregate(self):
        ans = aggregator.aggregate(
            Fixtures.slice_,
            Fixtures.pog, spender_values=set([None]),
            breakdown_keys=[
                Fixtures.dept, Fixtures.cofog,
                # Omit Fixtures.pog, Fixtures.region,
            ])
        assert ans, ans
        assert ans['metadata'] == {'axes': [u'dept', u'function']}, ans
        index = dict([(coords, amount) for (amount, coords) in ans['results']])
        for amount, coords in [
            (608.90, (u'999', u'6. Housing and community amenities')),
            (-9.20, (u'Dept004', u'of which: transport')),
            (-70.70, (u'Dept022', u'10. Social protection')),
            (-120.80, (u'Dept032', u'10. Social protection')),
            (-36.20, (u'Dept032', u'of which: employment policies')),
            (-0.50, (u'Dept047', u'3. Public order and safety')),
        ]:
            assert index.has_key(coords), coords
            # Tolerate rounding errors.
            assert abs(index[coords] - amount) < 0.01, (coords, amount)
    
    def test_fast_aggregate(self):
        ans = aggregator.fast_aggregate(
            Fixtures.slice_,
            Fixtures.pog, spender_values=set(['yes']),
            breakdown_keys=[
                Fixtures.dept, Fixtures.cofog,
                # Omit Fixtures.pog, Fixtures.region,
            ])
        assert ans, ans
        assert ans['metadata'] == {'axes': [u'dept', u'function']}, ans
        index = dict([(coords, amount) for (amount, coords) in ans['results']])
        for amount, coords in [
            (608.90, (u'999', u'6. Housing and community amenities')),
            (-9.20, (u'Dept004', u'of which: transport')),
            (-70.70, (u'Dept022', u'10. Social protection')),
            (-120.80, (u'Dept032', u'10. Social protection')),
            (-36.20, (u'Dept032', u'of which: employment policies')),
            (-0.50, (u'Dept047', u'3. Public order and safety')),
        ]:
            assert index.has_key(coords), coords
            # Tolerate rounding errors.
            assert abs(index[coords] - amount) < 0.01, (coords, amount)

