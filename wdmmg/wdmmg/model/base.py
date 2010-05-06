try:
    import json
except:
    import simplejson as json
from sqlalchemy.orm import class_mapper
import sqlalchemy.types as types


class DomainObject(object):
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)
    
    def as_dict(self):
        '''
        Returns a summary of this DomainObject suitable for inclusion in a
        JSON list of search results. The summary should include most fields
        of the domain object, but may omit potentially large fields such as
        `notes`. Foreign keys should be included as ids only.
        
        Link tables may be treated as part of one of the tables that they link.
        In particular, KeyValues attached to this DomainObject may be
        considered part of it, and therefore included in the result returned by
        this method.
        
        The default implementation returns a dict with only the key 'id'.
        '''
        return {'id': self.id}

    def __unicode__(self):
        fields = u', '.join([u'%s=%r' % (k, v) for k, v in self.as_dict().items()])
        return u'%s(%s, ...)' % (self.__class__.__name__, fields)

    def __str__(self):
        return self.__unicode__().encode('utf8')


class PublishedDomainObject(DomainObject):
    def as_big_dict(self):
        '''
        Returns detailed information about this DomainObject in a form suitable
        for converting to JSON. All fields should be included, and foreign keys
        should generally be replaced by the `as_dict()` representation of their
        referrent.
        
        The default implementation returns `self.as_dict()`.
        '''
        return self.as_dict()


class JsonType(types.TypeDecorator):
    '''Store data as JSON serializing on save and unserializing on use.
    '''
    impl = types.UnicodeText

    def process_bind_param(self, value, engine):
        if value is None or value == {}: # ensure we stores nulls in db not json "null"
            return None
        else:
            # ensure_ascii=False => allow unicode but still need to convert
            return unicode(json.dumps(value, ensure_ascii=False))

    def process_result_value(self, value, engine):
        if value is None:
            return None
        else:
            return json.loads(value)

    def copy(self):
        return JsonType(self.impl.length)

