import logging

from pylons import request, response, session, tmpl_context as c, url, app_globals
from pylons.controllers.util import abort, redirect
from pylons.decorators.cache import beaker_cache

from wdmmg.lib.base import BaseController, render
import wdmmg.model as model
from wdmmg.lib.helpers import Page

log = logging.getLogger(__name__)

class PogController(BaseController):
    @beaker_cache(type='dbm', query_args=True,
        invalidate_on_startup=True, # So we can still develop.
        # expire=864000, # 10 days.
    )
    def index(self):
        # c.items_per_page = 100
        page=int(request.params.get('page', 1))
        c.name = u'programme_object_group_code'
        c.codes = self._db.coins.distinct(c.name)
        def code_count(code):
            return self._db.coins.find({c.name:code},[c.name]).count()
        def get_desc(code):
            colname = c.name.replace('_code','_description')
            out = self._db.coins.find_one({c.name: code},
                    [colname])
            if colname in out:
                return out[colname]
            else:
                return None
        c.results = [ [code,get_desc(code),code_count(code)] for code in
                c.codes ]
        c.page = Page(
            collection=c.results,
            page=page,
            items_per_page=len(c.results),
        )
        return render('pog/index.html')

    def view(self, id):
        c.entry= self._db.coins.find_one({'srcid': id})
        if not c.entry:
            abort(404)
        return render('coins/entry.html')

