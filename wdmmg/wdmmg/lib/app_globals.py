from pymongo.connection import Connection
from pymongo.errors import ConnectionFailure
from pylons import config

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
        try:
            # conn = Connection(db_info['host'], db_info['port'],
            #                  pool_size=int(config['blog.database.pool']))
            conn = Connection("localhost", 27017)
        except ConnectionFailure:
            raise Exception('Unable to connect to MongoDB')
        dbname = config.get('mongodb.dbname', 'coins')
        self.db = conn[dbname]
        # auth = self.db.authenticate(db_info['username'], db_info['password'])
        # if not auth:
        #    raise Exception('Authentication to MongoDB failed')

