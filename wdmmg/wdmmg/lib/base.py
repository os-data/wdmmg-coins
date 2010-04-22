"""The base Controller API

Provides the BaseController class for subclassing.
"""
from pylons.controllers import WSGIController
from pylons.templating import render_genshi as render
from pylons import tmpl_context as c, request, config

import wdmmg
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

