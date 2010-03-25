import uuid

from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.types import *
from sqlalchemy.orm import mapper, relation, backref

import meta
from base import DomainObject
from keyvalue import add_keyvalues

class Slice(DomainObject):
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }

class Account(DomainObject):
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }

class Transaction(DomainObject):
    @classmethod
    def create_with_postings(cls, slice_, timestamp, amount, src, dest):
        txn = cls(slice_=slice_, timestamp=timestamp)
        srcposting = Posting(timestamp=timestamp, amount=-amount, account=src, transaction=txn)
        destposting = Posting(timestamp=timestamp, amount=amount, account=dest, transaction=txn)
        return txn

class Posting(DomainObject):
    pass


make_uuid = lambda: unicode(uuid.uuid4())

table_slice = Table('slice', meta.metadata,
    Column('id', UnicodeText(), primary_key=True, default=make_uuid),
    Column('name', UnicodeText(), unique=True),
    Column('notes', UnicodeText()),
)

table_account = Table('account', meta.metadata,
    Column('id', UnicodeText(), primary_key=True, default=make_uuid),
    Column('slice_id', UnicodeText(), ForeignKey('slice.id')),
    Column('name', UnicodeText()),
    Column('notes', UnicodeText()),
    )

table_transaction = Table('transaction', meta.metadata,
    Column('id', UnicodeText(), primary_key=True, default=make_uuid),
    Column('slice_id', UnicodeText(), ForeignKey('slice.id')),
    Column('timestamp', DateTime()),
    Column('notes', UnicodeText()),
    )

table_posting = Table('posting', meta.metadata,
    Column('id', UnicodeText(), primary_key=True, default=make_uuid),
    Column('timestamp', DateTime()),
    Column('amount', Float()),
    Column('account_id', UnicodeText(), ForeignKey('account.id'), index=True),
    Column('transaction_id', UnicodeText(), ForeignKey('transaction.id'), index=True),
    # Constraint: account.slice_ == transaction.slice_
    )


mapper(Slice, table_slice,
    order_by=table_slice.c.name
    )

mapper(Account, table_account, properties={
        'slice_': relation(Slice, backref=backref('accounts')),
        },
    order_by=table_account.c.id
    )

mapper(Transaction, table_transaction, properties={
        'slice_': relation(Slice, backref=backref('transactions')),
        },
    order_by=table_transaction.c.timestamp
    )

mapper(Posting, table_posting, properties={
        'transaction': relation(Transaction, backref=backref('postings')),
        'account': relation(Account, backref=backref('postings',
            order_by=table_posting.c.timestamp))
        },
    order_by=table_posting.c.id
    )

add_keyvalues(Account)
add_keyvalues(Transaction)
add_keyvalues(Posting)

