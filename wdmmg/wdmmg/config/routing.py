"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from pylons import config
from routes import Mapper

def make_map():
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'], explicit=True)
    map.minimization = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')

    # CUSTOM ROUTES HERE

    map.connect('home', '/', controller='home', action='index')

    map.connect('/slice', controller='slice', action='index')
    map.connect('/slice/{id}', controller='slice', action='view')
    map.connect('/slice/{action}/{id}', controller='slice')

    map.connect('/account', controller='account', action='index')
    map.connect('/account/{id}', controller='account', action='view')
    map.connect('/account/{action}/{id}', controller='account')

    map.connect('/transaction', controller='transaction', action='index')
    map.connect('/transaction/{id}', controller='transaction', action='view')
    map.connect('/transaction/{action}/{id}', controller='transaction')

    map.connect('/api', controller='api', action='index')
    map.connect('/api/{action}', controller='api')

    return map
