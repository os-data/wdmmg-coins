from datetime import datetime
from StringIO import StringIO

from sqlalchemy.orm import eagerload
from sqlalchemy.sql.expression import and_

import wdmmg.model as model

class Results:
    '''
    Represents the result of a call to `aggregate()`. This class has the
    following fields:
    
    dates - a list of the distinct transaction dates. These are unicode strings,
        and they are returned in sorted order.
    
    axes - a list of key names.
    
    matrix - a sparse matrix. This takes the form of a list of (coordinates,
        time series) pairs. The "coordinates" are a list giving the values of
        the Keys in the same order as they appear in `axes`. If no KeyValue
        exists for a given Key, the value `None` is supplied. The "time series"
        is a list of spending totals, one for each date in `dates`. If there
        was no spending on a given date, then `0.0` is supplied.
    '''
    
    def __init__(self, dates, axes, matrix=None):
        '''
        Do not construct a Results directly - call `aggregate()` instead.
        
        dates - a sorted list of unicode strings, representing all the distinct
            transaction dates needed.
        
        axes - a list of unicode strings, representing Key names.
        '''
        self.dates = dates
        self.date_index = dict([(date, index)
            for index, date in enumerate(self.dates)])
        self.axes = axes
        self.axis_index = dict([(axis, i) for i, axis in enumerate(axes)])
        self.matrix = matrix or {}
    
    def _add_spending(self, coordinates, amount, timestamp):
        '''
        For use by `aggregate()`.
        '''
        if coordinates not in self.matrix:
            self.matrix[coordinates] = [0.0] * len(self.dates)
        self.matrix[coordinates][self.date_index[timestamp]] += amount
    
    def divide_by_statistic(self, axis, statistic):
        '''
        Divides spending by a property of a coordinate. This is useful for
        computing statistics such as per-capita spending.
        
        axis - a Key, representing the coordinate to use, e.g. region.
        
        statistic - a Key, representing the statistic to use, e.g. population.
        
        The Key `axis` selects a property of Accounts (e.g. geographical
        region). The value of that property (e.g. 'NORTHERN IRELAND') is
        retrieved for each Account. Then, the Key `statistic` selects a
        property of those values (e.g. population). Finally, the aggregated
        spending is divided by the aggregated statistic. There are two cases,
        depending on whether `axis` is in `self.axes`:
        
         - If it is, then each spending item is divided by e.g. the population
        of its own region.
        
         - If it is not, then each spending item is divided by e.g. the total
        population of all regions.
        '''
        def to_float(x):
            try: return float(x)
            except ValueError: return None
        index = dict([
            (ev.code, to_float(ev.keyvalues[statistic]))
            for ev in model.Session.query(model.EnumerationValue).filter_by(key=axis)
            if statistic in ev.keyvalues
        ])
        if axis.name in self.axes:
            n = self.axis_index[axis.name] # Which coordinate?
            for coordinates, amounts in self.matrix.items():
                divisor = index.get(coordinates[n])
                for i in range(len(self.dates)):
#                    print "Dividing %r by %r" % (amounts[i], divisor)
                    if divisor and amounts[i] is not None: amounts[i] /= divisor
                    else: amounts[i] = None
        else:
            # FIXME: Does not work for hierarchical keys.
            divisor = sum(index.values())
            for coordinates, amounts in self.matrix.items():
                for i in range(len(self.dates)):
#                    print "Dividing %r by total %r" % (amounts[i], divisor)
                    if divisor and amounts[i] is not None: amounts[i] /= divisor
                    else: amounts[i] = None

    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return (
            'Results(\n\t%r,\n\t%r,\n\tmatrix=%r)' %
            (self.dates, self.axes, self.matrix)
        )

def aggregate(
    slice_,
    exclude=[], # list((Key, unicode))
    include={}, # list((Key, unicode))
    axes=[], # list(Key)
    start_date=u'1000', # Early enough?
    end_date=u'3000', # Late enough?
):
    '''
    Returns the dataset `slice_`, converted to a pivot table. The conversion
    consists of two steps:
    
    1. Draw a boundary between the "inside" and the "outside" of the spending 
    body, and keep only Transactions that cross the boundary. This is
    essentially a filter on postings.
    
    2. Classify the Transactions according to the properties of the Accounts 
    outside the boundary, and summarise the data by summing over all variables 
    apart from those of interest.
    
    Arguments:
    
    slice_ - a Slice object representing the dataset of interest.
    
    exclude - rules for excluding postings. This is a list of (key, value)
        pairs. A posting will be excluded if the value is a prefix
        of the posting's account's value for the key.
    
    include - rules for including postings. This is a list of (key, value)
        pairs. A posting will be excluded unless the value is a prefix
        of the posting's account's value for the key.
    
    axes - a list of Key objects representing the desired axes of the pivot
        table.
    
    start_date - a unicode string representing a date.
        Transactions before this date (string comparison) are ignored.
        Default: u'1000'.
    
    end_date - a unicode string representing a date.
        Transactions after this date (string comparison) are ignored.
        Default: u'3000'.
    
    Note that the timestamp that matters is the one on the Transaction object; 
    the timestamps of the individual Postings are ignored.
    
    Returns a Results object.
    '''
    assert isinstance(start_date, unicode), start_date
    assert isinstance(end_date, unicode), end_date
    query, params = _make_aggregate_query(
        slice_,
        exclude,
        include,
        axes,
        start_date,
        end_date
    )
#    print query
#    for k, v in params.items():
#        print k, v
    results = list(model.Session.execute(query, params))
    dates = sorted(set([row.timestamp for row in results]))
    ans = Results(dates, [key.name for key in axes])
    for row in results:
        ans._add_spending(
            tuple([row[i] for i in range(len(axes))]),
            row['amount'],
            row['timestamp'],
        )
    return ans

def _make_aggregate_query(
    slice_,
    exclude,
    include,
    axes,
    start_date,
    end_date
):
    '''
    Uses string manipulation to construct the SQL query needed by
    `aggregate()`.
    
    Parameters: same as `aggregate()`.
    Returns: (string, dict) pair representing the query and its params.
    '''
    # Compute some useful strings for each breakdown key.
    bds = [{
        'id': key.id, # The database `id` of the Key.
        'param': 'ak_%d' % i, # The SQL bind parameter whose value is `id`.
        'name': 'axis_%d' % i, # The SQL alias used for this coordinate.
    } for i, key in enumerate(axes)]

    # Compile an SQL query and its bind parameters at the same time.
    query, params = StringIO(), {}
    subselect_count = [0] # Use a singleton list for a mutable up-value.

    def write_subselect(key, value):
        '''
        Writes a sub-query that selects a set of account IDs, based on the
        value of a key. The query is a prefix search.
        
        key - a Key object
        value - a unicode string that should be a prefix of the value.
        '''
        # Update counter, and choose unambiguous SQL bind parameter names.
        n = subselect_count[0]
        subselect_count[0] += 1
        kv = {
            'k_param': 'k_%d' % n, # The SQL bind parameter whose value is `key.id`.
            'v_param': 'v_%d' % n, # The SQL bind parameter whose value is `value`.
        }
        # Write the sub-select query.
        query.write('''(SELECT object_id FROM key_value
    WHERE key_id = :%(k_param)s AND value = :%(v_param)s)''' % kv)
        params[kv['k_param']] = key.id
        params[kv['v_param']] = value

    # SELECT
    query.write('''\
SELECT''')
    for bd in bds:
        query.write('''
    (SELECT value FROM key_value WHERE object_id = a.id
        AND key_id = :%(param)s) AS %(name)s,''' % bd)
        params[bd['param']] = bd['id']
    query.write('''
    SUM(p.amount) as amount,
    t.timestamp''')
    # FROM
    query.write('''
FROM account a, posting p, "transaction" t''')
    # WHERE
    query.write('''
WHERE a.slice_id = :slice_id''')
    params['slice_id'] = slice_.id
    query.write('''
AND a.id = p.account_id''')
    for key, value in exclude:
        query.write('''
AND a.id NOT IN ''')
        write_subselect(key, value)
    for key, value in include:
        query.write('''
AND a.id IN ''')
        write_subselect(key, value)
    query.write('''
AND t.id = p.transaction_id
AND t.timestamp >= :start_date
AND t.timestamp <= :end_date''')
    params['start_date'] = start_date
    params['end_date'] = end_date
    # GROUP BY
    query.write('''
GROUP BY t.timestamp''')
    for bd in bds:
        query.write(', %(name)s' % bd)
    # ORDER BY
    query.write('''
ORDER BY t.timestamp''')
    for bd in bds:
        query.write(', %(name)s' % bd)

    return (query.getvalue(), params)

# Following attempt to alchemise the raw SQL fails.
# Problem is that the sub-query `dept_sq` has a free variable
# (`model.Account.id`). This variable is meant to be bound by the enclosing
# query. SQLAlchemy is not happy to leave it free in the sub-query, and
# magically introduces an unwanted join in order to bind it.
'''
spender_key = model.Session.query(model.Key).filter_by(name=u'spender').one()
dept_key = model.Session.query(model.Key).filter_by(name=u'dept').one()

spender_sq = (model.Session.query(model.KeyValue.object_id)
    .filter_by(key=spender_key)
    .filter_by(value=u'yes')
    ).subquery()
dept_sq = (model.Session.query(model.KeyValue.value)
    .filter_by(key=dept_key)
    .filter(model.KeyValue.object_id == model.Account.id) # FIXME: Wrong Account.
    ).subquery()

query = (model.Session.query(
        func.sum(model.Posting.amount),
        dept_sq.alias('dept'))
    .join(model.Account)
    .filter(~model.Account.id.in_(spender_sq))
    .group_by('dept')
    )
'''

