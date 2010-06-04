"""The base Controller API

Provides the BaseController class for subclassing.
"""
import pylons
from pylons.controllers import WSGIController
from pylons.templating import render_genshi as render
from pylons import tmpl_context as c, request, config
from pylons.controllers.util import abort

import wdmmg
from wdmmg import model
from wdmmg.model import meta

class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        try:
            self._db = pylons.app_globals.db
            return WSGIController.__call__(self, environ, start_response)
        finally:
            meta.Session.remove()
    
    def __before__(self, action, **params):
        c.__version__ = wdmmg.__version__
        c.site_title = config.get('site_title', 'Where Does My Money Go? Store')
        c.items_per_page = int(request.params.get('items_per_page', 20))
        c.default_slice = config.get('default_slice', u'cra')

    def get_by_id(self, domain_class, id_):
        ans = model.Session.query(domain_class).get(id_)
        if not ans:
            abort(404, 'No record with id %r'%id_)
        return ans
    
    def get_by_name_or_id(self, domain_class, name_or_id):
        ans = (model.Session.query(domain_class)
            .filter_by(name=name_or_id)
            ).first()
        if not ans:
            ans = model.Session.query(domain_class).get(name_or_id)
        if not ans:
            abort(404, 'No record with name or id %r' % name_or_id)
        return ans

