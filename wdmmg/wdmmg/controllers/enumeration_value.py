import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from wdmmg.lib.base import BaseController, render

from wdmmg import model

log = logging.getLogger(__name__)

class EnumerationValueController(BaseController):
    '''
    EnumerationValues are usually specified using a Key and a code.
    The Key is usually specified by `name`, though an `id` is also accepted.
    For backwards EnumerationValues can also be specified by `id`.
    '''

    def view_id(self, id_=None):
        '''Deprecated.'''
        c.row = self.get_by_id(model.EnumerationValue, id_)
        c.key = c.row.key
        return render('enumeration_value/view.html')

    def view(self, name_or_id=None, code=None):
        '''
        name_or_id - a `Key.name` or `Key.id`.
        code - an `EnumerationValue.code`.
        '''
        c.key = self.get_by_name_or_id(model.Key, name_or_id)
        c.row = (model.Session.query(model.EnumerationValue)
            .filter_by(key=c.key)
            .filter_by(code=code)
            ).first()
        q = model.Session.query(model.Account)
        q = q.join((model.KeyValue,
            model.KeyValue.object_id==model.Account.id))
        q = q.join(model.Key)
        q = q.join(model.EnumerationValue)
        print q.filter(model.Key.name==c.key.name)

        c.accounts = q.filter(model.EnumerationValue.id==c.row.id
                ).filter(model.Key.name==c.key.name,
                        ).distinct().all()
        
        if not c.row:
            abort(404, 'No record with code %r'%code)
        return render('enumeration_value/view.html')

