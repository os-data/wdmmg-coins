import uuid

from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.types import *
from sqlalchemy.orm import mapper, relation, backref

import meta
from base import DomainObject, PublishedDomainObject
from keyvalue import add_keyvalues

class Slice(PublishedDomainObject):
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    def as_big_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'notes': self.notes,
        }

class Account(PublishedDomainObject):
    def as_dict(self):
        return {
            'id': self.id,
            'slice_id': self.slice_id,
            'name': self.name,
            'keyvalues': dict([(key.name, value)
                for key, value in self.keyvalues.items()])
        }

    def as_big_dict(self):
        return {
            'id': self.id,
            'slice': self.slice.as_dict(),
            'name': self.name,
            'notes': self.notes,
            'keyvalues': dict([(key.name, value)
                for key, value in self.keyvalues.items()])
        }

class Transaction(PublishedDomainObject):
    @classmethod
    def create_with_postings(cls, slice_, timestamp, amount, src, dest,
            currency='gbp'):
        assert isinstance(timestamp, unicode)
        txn = cls(slice_=slice_, timestamp=timestamp)
        srcposting = Posting(timestamp=timestamp, amount=-amount, account=src, transaction=txn)
        destposting = Posting(timestamp=timestamp, amount=amount, account=dest, transaction=txn)
        return txn
    
    @property
    def amount(self):
        return sum([p.amount for p in self.postings if p.amount>0])

    def as_dict(self):
        return {
            'id': self.id,
            'slice_id': self.slice_id,
            'timestamp': self.timestamp,
            'postings': [{
                'timestamp': p.timestamp,
                'amount': p.amount,
                'currency': p.currency,
                'account_id': p.account_id,
            } for p in self.postings],
        }

    def as_big_dict(self):
        return {
            'id': self.id,
            'slice': self.slice.as_dict(),
            'name': self.name,
            'notes': self.notes,
            'postings': [{
                'timestamp': p.timestamp,
                'amount': p.amount,
                'currency': p.currency,
                'account': p.account.as_dict(),
            } for p in self.postings],
        }

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
    Column('timestamp', UnicodeText()),
    Column('notes', UnicodeText()),
    )

table_posting = Table('posting', meta.metadata,
    Column('id', UnicodeText(), primary_key=True, default=make_uuid),
    Column('timestamp', UnicodeText()),
    Column('amount', Float()),
    Column('currency', UnicodeText()),
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

