import logging
from datetime import datetime

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify

from wdmmg.lib.base import BaseController, render
from wdmmg import model

log = logging.getLogger(__name__)

# List of actions that can be performed on a domain object.
READ = u'READ'

class RestController(BaseController):

    def index(self):
        slice_ = model.Session.query(model.Slice).first()
        enumeration_value = model.Session.query(model.EnumerationValue).first()
        key = enumeration_value.key
        c.urls = [
            url(controller='rest', action='slice', name_or_id=slice_.name),
            url(controller='rest', action='slice', name_or_id=slice_.id),
            url(controller='rest', action='account',
                id_=model.Session.query(model.Account).first().id),
            url(controller='rest', action='transaction',
                id_=model.Session.query(model.Transaction).first().id),
            url(controller='rest', action='key', name_or_id=key.name),
            url(controller='rest', action='key', name_or_id=key.id),
            url(controller='rest', action='enumeration_value',
                name_or_id=enumeration_value.key.name, code=enumeration_value.code),
        ]
        return render('home/rest.html')
    
    @jsonify
    def slice(self, name_or_id=None):
        return self._domain_object(self.get_by_name_or_id(model.Slice, name_or_id))
        
    @jsonify
    def account(self, id_=None):
        return self._domain_object(self.get_by_id(model.Account, id_))
        
    @jsonify
    def transaction(self, id_=None):
        return self._domain_object(self.get_by_id(model.Transaction, id_))
        
    @jsonify
    def key(self, name_or_id=None):
        return self._domain_object(self.get_by_name_or_id(model.Key, name_or_id))
        
    @jsonify
    def enumeration_value_id(self, id_=None):
        '''Deprecated'''
        return self._domain_object(self.get_by_id(model.EnumerationValue, id_))
        
    @jsonify
    def enumeration_value(self, name_or_id=None, code=None):
        '''
        name_or_id - a `Key.name or a `Key.id`.
        code - an `EnumerationValue.code`.
        '''
        key = self.get_by_name_or_id(model.Key, name_or_id)
        ev = (model.Session.query(model.EnumerationValue)
            .filter_by(key=key)
            .filter_by(code=code)
            ).first()
        return self._domain_object(ev)

    def _domain_object(self, domain_object):
        self._check_access(domain_object, READ)
        return domain_object.as_big_dict()

    def _check_access(self, domain_object, action):
        '''
        Checks whether the supplied `apikey` permits `action` to be performed
        on `domain_object`. If allowed, returns `True`. If forbidden, throws
        an appropriate HTTPException.
        '''
        if action == READ:
            return True
        abort(403)

