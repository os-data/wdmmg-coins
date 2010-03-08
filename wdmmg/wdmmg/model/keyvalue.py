
import uuid

from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.types import *
from sqlalchemy.orm import mapper, relation, backref

import meta
from base import DomainObject

class Key(DomainObject):
    pass

class EnumerationValue(DomainObject):
    pass

class KeyValue(DomainObject):
    def __init__(self, domain_object, key, value):
        self.domain_object = domain_object
        self.key = key
        assert isinstance(value, basestring)
        self.value = value


make_uuid = lambda: unicode(uuid.uuid4())
table_key = Table('key', meta.metadata,
    Column('id', UnicodeText(), primary_key=True, default=make_uuid),
    Column('name', UnicodeText()),
    Column('description', UnicodeText()),
    )

table_enumeration_value = Table('enumeration_value', meta.metadata,
    Column('key_id', UnicodeText(), ForeignKey('key.id'), primary_key=True),
    Column('name', UnicodeText(), primary_key=True),
    )

table_key_value = Table('key_value', meta.metadata,
    Column('id', UnicodeText(), primary_key=True, default=make_uuid),
    Column('ns', UnicodeText()),
    Column('object_id', UnicodeText()),
    Column('key_id', UnicodeText(), ForeignKey('key.id')),
    Column('value', UnicodeText()),
    )


mapper(Key, table_key,
    order_by=table_key.c.id
    )

mapper(EnumerationValue, table_enumeration_value, properties={
    'key': relation(Key, backref='enumeration_values'),
    },
    order_by=[table_enumeration_value.c.key_id,table_enumeration_value.c.name]
    )

mapper(KeyValue, table_key_value, properties={
    'key': relation(Key, backref='key_values'),
    #'subject': relation(
    },
    order_by=table_key_value.c.id
    )


