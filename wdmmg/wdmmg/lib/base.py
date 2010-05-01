"""The base Controller API

Provides the BaseController class for subclassing.
"""
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
            return WSGIController.__call__(self, environ, start_response)
        finally:
            meta.Session.remove()
    
    def __before__(self, action, **params):
        c.__version__ = wdmmg.__version__
        c.site_title = config.get('site_title', 'Where Does My Money Go? Store')
        c.items_per_page = int(request.params.get('items_per_page', 20))

    def get_by_id(self, domain_class, id_):
        ans = model.Session.query(domain_class).get(id_)
        if not ans:
            abort(404, 'No record with id %r'%id_)
        return ans
    
    def get_by_id_or_name(self, domain_class, id_or_name):
        ans = model.Session.query(domain_class).get(id_or_name)
        if not ans:
            ans = (model.Session.query(domain_class)
                .filter_by(name=id_or_name)
                ).first()
        if not ans:
            abort(404, 'No record with id %r' % id_or_name)
        return ans

