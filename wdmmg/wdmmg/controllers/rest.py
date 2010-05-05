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
        c.urls = {
            'slice': url(controller='rest', action='slice',
                name_or_id=model.Session.query(model.Slice).first().name),
            'slice-id': url(controller='rest', action='slice',
                name_or_id=model.Session.query(model.Slice).first().id),
            'account': url(controller='rest', action='account',
                id_=model.Session.query(model.Account).first().id),
            'transaction': url(controller='rest', action='transaction',
                id_=model.Session.query(model.Transaction).first().id),
            'key': url(controller='rest', action='key',
                name_or_id=model.Session.query(model.Key).first().name),
            'key-id': url(controller='rest', action='key',
                name_or_id=model.Session.query(model.Key).first().id),
            'enumeration_value': url(controller='rest', action='enumeration_value',
                id_=model.Session.query(model.EnumerationValue).first().id),
        }
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
    def enumeration_value(self, id_=None):
        return self._domain_object(self.get_by_id(model.EnumerationValue, id_))
        
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

