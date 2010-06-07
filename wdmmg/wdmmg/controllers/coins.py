import logging

from pylons import request, response, session, tmpl_context as c, url, app_globals
from pylons.controllers.util import abort, redirect

from wdmmg.lib.base import BaseController, render
import wdmmg.model as model
from wdmmg.lib.helpers import Page

log = logging.getLogger(__name__)

class CoinsController(BaseController):

    def index(self):
        return self.index_solr()

    def index_solr(self):
        c.items_per_page = 100
        c.q = request.params.get('q', None)
        page=int(request.params.get('page', 1))
        if c.q:
            ourq = ' AND '.join(c.q.split())
            query = app_globals.solr.query(ourq, rows=c.items_per_page)
        else:
            query = app_globals.solr.query('*', sort='score desc, value desc', rows=c.items_per_page)
        c.results = query.results
        c.page = Page(
            collection=c.results,
            page=page,
            items_per_page=c.items_per_page,
            item_count=query.numFound,
            q=c.q, # Preserve `q` when the user clicks 'next' or 'previous'.
        )
        return render('coins/index.html')



    def index_mongo(self):
        from pymongo import ASCENDING, DESCENDING
        c.items_per_page = 100
        c.q = request.params.get('q', None)
        page=int(request.params.get('page', 1))
        if c.q:
            # textq = '/.*%s.*/i' % c.q
            dbq = self._db.coins.find(
                    {'search_field':{'$all': c.q.split()}}
                    )
            dbq.sort('value', DESCENDING)
        else:
            dbq = self._db.coins.find().sort('value', DESCENDING)
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


    def view(self, id):
        c.entry= self._db.coins.find_one({'srcid': id})
        if not c.entry:
            abort(404)
        return render('coins/entry.html')

