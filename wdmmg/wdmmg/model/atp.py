import uuid

from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.types import *
from sqlalchemy.orm import mapper, relation, backref

import meta
from base import DomainObject


class Account(DomainObject):
    pass

class Transaction(DomainObject):
    @classmethod
    def create_with_postings(cls, timestamp, amount, src, dest):
        txn = cls(timestamp=timestamp)
        srcposting = Posting(timestamp=timestamp, amount=amount, account=src, transaction=txn)
        destposting = Posting(timestamp=timestamp, amount=-amount, account=dest, transaction=txn)
        return txn

class Posting(DomainObject):
    pass


make_uuid = lambda: unicode(uuid.uuid4())
table_account = Table('account', meta.metadata,
    Column('id', UnicodeText(), primary_key=True, default=make_uuid),
    Column('name', UnicodeText()),
    Column('notes', UnicodeText()),
    )

table_transaction = Table('transaction', meta.metadata,
    Column('id', UnicodeText(), primary_key=True, default=make_uuid),
    Column('timestamp', DateTime()),
    Column('notes', UnicodeText()),
    )

table_posting = Table('posting', meta.metadata,
    Column('id', UnicodeText(), primary_key=True, default=make_uuid),
    Column('timestamp', DateTime()),
    Column('amount', Float()),
    Column('account_id', UnicodeText(), ForeignKey('account.id')),
    Column('transaction_id', UnicodeText(), ForeignKey('transaction.id')),
    )


mapper(Account, table_account,
    order_by=table_account.c.id
    )
mapper(Transaction, table_transaction,
    order_by=table_transaction.c.timestamp
    )
mapper(Posting, table_posting, properties={
    'transaction': relation(Transaction, backref=backref('postings')),
    'account': relation(Account, backref=backref('postings',
        order_by=table_posting.c.timestamp))
    },
    order_by=table_posting.c.id
    )


