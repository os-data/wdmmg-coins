import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from wdmmg.lib.base import BaseController, render
import wdmmg.model as model
from wdmmg.lib.helpers import Page

log = logging.getLogger(__name__)

class CoinsController(BaseController):
    def __before__(self, action, **params):
        super(CoinsController, self).__before__(action, **params)
        import pymongo
        connection = pymongo.Connection("localhost", 27017)
        # dbname = 'coins'
        dbname = 'coins'
        self.db = connection[dbname]

    def index(self):
        c.items_per_page = 100
        c.q = request.params.get('q', None)
        page=int(request.params.get('page', 1))
        if c.q:
            # textq = '/.*%s.*/i' % c.q
            dbq = self.db.coins.find(
                    {'search_field':{'$all': c.q.split()}}
                    )
        else:
            dbq = self.db.coins.find()
        c.results = [ x for x in
                dbq.limit(c.items_per_page).skip((page-1)*c.items_per_page)
        ]
        c.page = Page(
            collection=c.results,
            page=page,
            items_per_page=c.items_per_page,
            item_count=dbq.count(),
            q=c.q, # Preserve `q` when the user clicks 'next' or 'previous'.
        )
        return render('coins/index.html')

