import uuid

from sqlalchemy import Table, Column, ForeignKey, and_
from sqlalchemy.types import *
from sqlalchemy.orm import mapper, relation, backref, class_mapper

import meta
from base import DomainObject, JsonType

class Key(DomainObject):
    pass

class EnumerationValue(DomainObject):
    pass

class KeyValue(DomainObject):
    pass

def add_keyvalues(domain_object, proxy_name='keyvalues',
        sqlalchemy_property_name='_keyvalues'):
    '''Add an attribute `proxy_name` and `sqlalchemy_property_name` to 
    `domain_object`.

    E.g.::
        add_keyvalues(Account, 'myproxyname', 'myproperty')
        # now ...
        acc = Account()
        acc.myproxyname[Key] = u'value'
        acc.myproperty[Key] = KeyValue(...)
        # also on KeyValue
        kv = KeyValue(account=...)
        kv.account 
    '''
    mapper = class_mapper(domain_object)
    table = mapper.local_table
    table_name = unicode(table.name)
    primaryjoin = and_(
        table_key_value.c.ns == table_name,
        table_key_value.c.object_id== list(table.primary_key)[0]
        )
    foreign_keys = [table_key_value.c.object_id]
    from sqlalchemy.orm.collections import attribute_mapped_collection
    mapper.add_property(sqlalchemy_property_name, relation(
        KeyValue,
        primaryjoin=primaryjoin,
        foreign_keys=foreign_keys,
        collection_class=attribute_mapped_collection('key'),
        backref='ns_'+domain_object.__name__.lower(),
        cascade='all, delete, delete-orphan'
        )
    )
    from sqlalchemy.ext.associationproxy import association_proxy
    def _create_keyvalue(key, value):
        return KeyValue(ns=table_name, key=key, value=value)
    setattr(domain_object, proxy_name,
            association_proxy(sqlalchemy_property_name, 'value', creator=_create_keyvalue)
            )


make_uuid = lambda: unicode(uuid.uuid4())
table_key = Table('key', meta.metadata,
    Column('id', UnicodeText(), primary_key=True, default=make_uuid),
    Column('name', UnicodeText(), unique=True),
    Column('notes', UnicodeText()),
    )

table_enumeration_value = Table('enumeration_value', meta.metadata,
    Column('id', UnicodeText(), primary_key=True, default=make_uuid),
    Column('key_id', UnicodeText(), ForeignKey('key.id')),
    Column('name', UnicodeText()),
    Column('notes', UnicodeText()),
    )

table_key_value = Table('key_value', meta.metadata,
    Column('id', UnicodeText(), primary_key=True, default=make_uuid),
    Column('ns', UnicodeText()),
    Column('object_id', UnicodeText(), index=True),
    Column('key_id', UnicodeText(), ForeignKey('key.id'), index=True),
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
        'enumeration_value': relation(
            EnumerationValue,
            primaryjoin=and_(
                table_key_value.c.key_id == table_enumeration_value.c.key_id,
                table_key_value.c.value == table_enumeration_value.c.name
            ),
            foreign_keys=[table_enumeration_value.c.key_id, table_enumeration_value.c.name],
            uselist=False
        ),
        # Relations on `object_id` can be created by `add_keyvalues()`.
    },
    order_by=table_key_value.c.id
    )

add_keyvalues(Key)
add_keyvalues(EnumerationValue)

