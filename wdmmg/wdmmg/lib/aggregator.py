from datetime import datetime
from StringIO import StringIO

from sqlalchemy.orm import eagerload
from sqlalchemy.sql.expression import and_

import wdmmg.model as model

def aggregate(
    slice_,
    spender_key, # TODO: Slice-dependent default.
    spender_values=set(['yes']),
    breakdown_keys=[],
    start_date=datetime(1000, 1, 1), # Early enough?
    end_date=datetime(3000, 1, 1), # Late enough?
):
    '''
    Returns the dataset `slice_`, converted to a pivot table. The conversion
    consists of two steps:
    
    1. Draw a boundary between the "inside" and the "outside" of the spending 
    body, and keep only Transactions that cross the boundary.
    
    2. Classify the Transactions according to the properties of the Accounts 
    outside the boundary, and summarise the data by summing over all variables 
    apart from those of interest.
    
    Arguments:
    
    slice_ - a Slice object representing the dataset of interest.
    
    spender_key - a Key object representing the criterion used to distinguish 
        Accounts "inside" the spending body from those "outside" it.
    
    spender_values - a set of the `spender_key` values representing Accounts 
        "inside" the spending body. `None` may be used to select Accounts with
        no value defined for `spender_key`.
    
    breakdown_keys - a list of Key objects representing the desired axes of 
        the pivot table.
    
    start_date - a DateTime object. Transactions before this date are ignored.
        Default: 01/01/1000.
    
    end_date - a DateTime object. Transactions on or after this date are 
        ignored. Default: now.
    
    Note that the timestamp that matters is the one on the Transaction object; 
    the timestamps of the individual Postings are ignored.
    '''
    # Populate Session with the relevant data in a small number of queries.
    # Accounts.
    account_filter = model.Account.slice_ == slice_
    all_accounts = (model.Session.query(model.Account)
        .filter(account_filter)
        ).all()
    # KeyValues.
    key_ids = set([spender_key.id])
    key_ids.update([k.id for k in breakdown_keys])
    all_key_values = (model.Session.query(model.KeyValue)
        .filter(model.KeyValue.key_id.in_(key_ids)) # Must use ids for in_().
        .join((model.Account, model.KeyValue.object_id == model.Account.id))
        .filter(account_filter)
        ).all()
    # Transactions.
    transaction_filter = and_(
        model.Transaction.slice_ == slice_,
        model.Transaction.timestamp >= start_date,
        model.Transaction.timestamp < end_date,
        )
    all_transactions = (model.Session.query(model.Transaction)
        .filter(transaction_filter)
        ).all()
    # Postings.
    all_postings = (model.Session.query(model.Posting)
        .join(model.Transaction)
        .filter(transaction_filter) 
        ).all()
    
    # Uncomment following line for deugging.
    # return (all_accounts, all_transactions, all_postings, all_key_values)
    
    # Loop through all Postings, examine Account, add to relevant bucket.
    buckets = {} # tuple of values -> float
    for p in all_postings:
        a = p.account
        if a.keyvalues.get(spender_key) not in spender_values:
            vs = tuple([a.keyvalues.get(k) for k in breakdown_keys])
            if vs not in buckets:
                buckets[vs] = 0.0
            buckets[vs] += p.amount
    
    # Sort and return.
    return {
        'metadata': {'axes': [k.name for k in breakdown_keys]},
        'results': [(amount, values) for values, amount in sorted(buckets.items())]
    }



def fast_aggregate(
    slice_,
    spender_key, # TODO: Slice-dependent default.
    spender_values=set(['yes']),
    breakdown_keys=[],
    start_date=datetime(1000, 1, 1), # Early enough?
    end_date=datetime(3000, 1, 1), # Late enough?
):
    '''
    A faster reimplementation of `aggregate()`
    '''
    query, params = _make_aggregate_query(
        slice_,
        spender_key,
        spender_values,
        breakdown_keys,
        start_date,
        end_date
    )
    results = model.Session.execute(query, params)
    return {
        'metadata': {'axes': [key.name for key in breakdown_keys]},
        'results': [
            (row['amount'], tuple([row[i] for i, _ in enumerate(breakdown_keys)]))
            for row in results
        ]
    }

def _make_aggregate_query(
    slice_,
    spender_key, # TODO: Slice-dependent default.
    spender_values,
    breakdown_keys,
    start_date,
    end_date
):
    '''
    Uses string manipulation to construct the SQL query needed by
    `fast_aggregate()`.
    
    Parameters: same as `fast_aggregate()`.
    Returns: (string, dict) representing the query and its params.
    '''
    # Compute some useful strings for each breakdown key.
    bds = [{
        'id': key.id, # The database 'id' of the Key.
        'param': 'bd_%d_id' % i, # The SQL bind parameter whose value is `id`.
        'name': 'bd_%d' % i, # The SQL alias used for this coordinate.
    } for i, key in enumerate(breakdown_keys)]
    # Compute some useful strings for each spender value.
    svs = [{
        'param': 'sv_%d' % i, # The SQL bind parameter whose value is `value`.
        'value': value, # The SQL literal value.
    } for i, value in enumerate(spender_values)]

    # Compile an SQL query and its bind parameters at the same time.
    query, params = StringIO(), {}
    # SELECT
    query.write('''\
SELECT
''')
    for bd in bds:
        query.write('''\
    (SELECT value FROM key_value WHERE object_id = a.id
        AND key_id = :%(param)s) AS %(name)s,
''' % bd)
        params[bd['param']] = bd['id']
    query.write('''\
    SUM(p.amount) as amount
''')
    # FROM
    # TODO: Join on transaction.
    query.write('''\
FROM account a, posting p, "transaction" t
''')
    # TODO: Filter on slice.id.
    # TODO: Filter on transaction.timestamp.
    # WHERE
    query.write('''\
WHERE a.slice_id = :slice_id
''')
    params['slice_id'] = slice_.id
    query.write('''\
AND a.id = p.account_id
AND a.id NOT IN (SELECT object_id FROM key_value
    WHERE key_id = :spender_key_id
''')
    params['spender_key_id'] = spender_key.id
    query.write('''\
    AND value IN (''')
    for sv in svs:
        query.write(':%(param)s, ' % sv)
        params[sv['param']] = sv['value']
    query.write('''NULL))
''') # Absorbs final comma; copes with len(svs)==0.
    query.write('''\
AND t.id = p.transaction_id
AND t.timestamp >= :start_date
AND t.timestamp < :end_date
''')
    params['start_date'] = start_date
    params['end_date'] = end_date
    # GROUP BY
    query.write('''\
GROUP BY ''')
    for bd in bds:
        query.write('%(name)s, ' % bd)
    query.write('''NULL
''') # Absorbs final comma; copes with len(bds)==0.
    # ORDER BY
    query.write('''\
ORDER BY ''')
    for bd in bds:
        query.write('%(name)s, ' % bd)
    query.write('''NULL
''') # Absorbs final comma; copes with len(bds)==0.

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

