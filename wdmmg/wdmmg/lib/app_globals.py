from pymongo.connection import Connection
from pymongo.errors import ConnectionFailure
from pylons import config
from solr import SolrConnection

class Globals(object):
    """Globals acts as a container for objects available throughout the
    life of the application

    """
    def __init__(self):
        """One instance of Globals is created during application
        initialization and is available during requests via the
        'app_globals' variable

        """
        # Populate basic app globals
        ipaddr = config['mongodb.host']
        pool_size = config['mongodb.pool_size']
        try:
            # conn = Connection(db_info['host'], db_info['port'],
            #                  pool_size=int(config['blog.database.pool']))
            conn = Connection(ipaddr, 27017, pool_size=pool_size)
        except ConnectionFailure:
            raise Exception('Unable to connect to MongoDB')
        dbname = config.get('mongodb.db_name')
        self.db = conn[dbname]
        # auth = self.db.authenticate(db_info['username'], db_info['password'])
        # if not auth:
        #    raise Exception('Authentication to MongoDB failed')
        self.solr_url = config.get('solr.url', 'http://localhost:8080/solr')
        self.solr = SolrConnection(self.solr_url)
        # self.cache = CacheManager(**parse_cache_config_options(config))


