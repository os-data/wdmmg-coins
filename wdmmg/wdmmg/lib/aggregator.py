from datetime import datetime
from sqlalchemy.orm import eagerload
from sqlalchemy.sql.expression import and_

import wdmmg.model as model

def aggregate(
    slice_,
    spender_key,
    start_date=datetime(1000, 1, 1), # Early enough?
    end_date=datetime.now(),
    spender_values=set([None]),
    breakdown_keys=[]
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
    
    start_date - a DateTime object. Transactions before this date are ignored.
        Default: 01/01/1000.
    
    end_date - a DateTime object. Transactions on or after this date are 
        ignored. Default: now.
    
    spender_values - a set of the `spender_key` values representing Accounts 
        "inside" the spending body. `None` may be used to select Accounts with
        no value defined for `spender_key`.
    
    breakdown_keys - a list of Key objects representing the desired axes of 
        the pivot table.
    
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
    
    # Uncomment following line for testing.
    return (all_accounts, all_transactions, all_postings, all_key_values)

# For debugging
'''
model.repo.delete_all()
model.Session.commit()
import wdmmg.tests.test_craloader as cra
cra.CRALoader.load(cra.pkg_resources.resource_stream('wdmmg', 'tests/cra_2009_db_short.csv'))
model.Session.commit()
slice_ = model.Session.query(model.Slice).filter_by(name=u'cra').one()
key = model.Session.query(model.Key).filter_by(name=u'pog').one()
'''

