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
    
    map.connect('/aggregate', controller='aggregate', action='view')

    map.connect('/slice', controller='slice', action='index')
    map.connect('/slice/{name_or_id}', controller='slice', action='view')
    map.connect('/slice/{name_or_id}/{action}', controller='slice')

    map.connect('/account', controller='account', action='index')
    map.connect('/account/search', controller='account', action='search')
    map.connect('/account/{id_}', controller='account', action='view')
    map.connect('/account/{id_}/{action}', controller='account')

    map.connect('/transaction', controller='transaction', action='index')
    map.connect('/transaction/{id_}', controller='transaction', action='view')
    map.connect('/transaction/{id_}/{action}', controller='transaction')

    map.connect('/key', controller='key', action='index')
    map.connect('/key/{name_or_id}', controller='key', action='view')
    map.connect('/key/{name_or_id}/{action}', controller='key')
    map.connect('/key/{name_or_id}/value/{code}', controller='enumeration_value', action='view')
    map.connect('/key/{name_or_id}/value/{code}/{action}', controller='enumeration_value')

    # Deprecated.
    map.connect('/enumeration_value/{id_}', controller='enumeration_value', action='view_id')

    map.connect('/api', controller='api', action='index')
    map.connect('/api/aggregate', controller='api', action='aggregate')
    map.connect('/api/mytax', controller='api', action='mytax')

    map.connect('/api/rest', controller='rest', action='index')
    map.connect('/api/rest/slice/{name_or_id}', controller='rest', action='slice')
    map.connect('/api/rest/account/{id_}', controller='rest', action='account')
    map.connect('/api/rest/transaction/{id_}', controller='rest', action='transaction')
    map.connect('/api/rest/key/{name_or_id}', controller='rest', action='key')
    map.connect('/api/rest/key/{name_or_id}/value/{code}', controller='rest', action='enumeration_value')
    map.connect('/api/rest/enumeration_value/{id_}', controller='rest', action='enumeration_value_id')

    return map
