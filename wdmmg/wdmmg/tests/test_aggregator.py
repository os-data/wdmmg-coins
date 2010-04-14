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
            exclude=[(Fixtures.spender, u'yes')],
            include=[(Fixtures.region, 'ENGLAND')],
            axes=[
                Fixtures.dept, Fixtures.cofog,
                # Omit Fixtures.pog, Fixtures.region,
            ])
        print ans
        assert ans, ans
        dates, axes, matrix = ans
        assert axes == [u'dept', u'function'], axes
        index = dict([(coords, sum(amount)) for (coords, amount) in matrix])
        for k, v in index.items():
            print k, v
        assert len(index) == 6, index
        for amount, coords in [
            (-608.90, (u'999', u'6. Housing and community amenities')),
            (9.20, (u'Dept004', u'of which: transport')),
            (70.70, (u'Dept022', u'10. Social protection')),
            (120.80, (u'Dept032', u'10. Social protection')),
            (-0.10, (u'Dept032', u'of which: employment policies')),
            (0.50, (u'Dept047', u'3. Public order and safety')),
        ]:
            assert index.has_key(coords), coords
            # Tolerate rounding errors.
            assert abs(index[coords] - amount) < 0.01, (coords, amount)
    
    def test_aggregate_dates(self):
        ans = aggregator.aggregate(
            Fixtures.slice_,
            exclude=[(Fixtures.spender, u'yes')],
            include=[(Fixtures.region, 'ENGLAND')],
            axes=[
                Fixtures.dept, Fixtures.cofog,
                # Omit Fixtures.pog, Fixtures.region,
            ],
            start_date=date(2008, 01, 01),
            end_date=date(2009, 01, 01))
        assert ans, ans
        dates, axes, matrix = ans
        assert axes == [u'dept', u'function'], axes
        index = dict([(coords, amounts[0]) for (coords, amounts) in matrix])
        for k, v in index.items():
            print k, v
        assert len(index) == 5, index
        for amount, coords in [
            (-20.60, (u'999', u'6. Housing and community amenities')),
            (1.30, (u'Dept004', u'of which: transport')),
            (0.10, (u'Dept047', u'3. Public order and safety')),
            (30.40, (u'Dept032', u'10. Social protection')),
            (0.10, (u'Dept022', u'10. Social protection')),
        ]:
            assert index.has_key(coords), coords
            # Tolerate rounding errors.
            assert abs(index[coords] - amount) < 0.01, (coords, amount)

    def test_make_aggregate_query(self):
        query, params = aggregator._make_aggregate_query(
            Fixtures.slice_,
            exclude=[(Fixtures.spender, u'yes')],
            include=[(Fixtures.region, 'ENGLAND')],
            axes=[
                Fixtures.dept, Fixtures.cofog,
                # Omit Fixtures.pog, Fixtures.region,
            ],
            start_date=date(2008, 01, 01),
            end_date=date(2009, 01, 01))
        print query
        print params
        assert query == '''\
SELECT
    (SELECT value FROM key_value WHERE object_id = a.id
        AND key_id = :ak_0) AS axis_0,
    (SELECT value FROM key_value WHERE object_id = a.id
        AND key_id = :ak_1) AS axis_1,
    SUM(p.amount) as amount,
    t.timestamp
FROM account a, posting p, "transaction" t
WHERE a.slice_id = :slice_id
AND a.id = p.account_id
AND a.id NOT IN (SELECT object_id FROM key_value
    WHERE key_id = :k_0 AND value LIKE :v_0)
AND a.id IN (SELECT object_id FROM key_value
    WHERE key_id = :k_1 AND value LIKE :v_1)
AND t.id = p.transaction_id
AND t.timestamp >= :start_date
AND t.timestamp < :end_date
GROUP BY t.timestamp, axis_0, axis_1
ORDER BY t.timestamp, axis_0, axis_1''', query

# TODO: Test filtering on slice.
# TODO: Test filtering on timestamp.
# TODO: Test with some breakdown KeyValues missing.

