import logging

from pylons import request, response, session, tmpl_context as c, url, app_globals
from pylons.controllers.util import abort, redirect
from pylons.decorators.cache import beaker_cache

from wdmmg.lib.base import BaseController, render
import wdmmg.model as model
from wdmmg.lib.helpers import Page

log = logging.getLogger(__name__)

class FacetController(BaseController):

    def index(self):
        return render('facet/index.html')

    @beaker_cache(type='dbm', query_args=True,
        invalidate_on_startup=True, # So we can still develop.
        expire=8640000, # 10 days.
    )
    def view(self, year, field):
        dataset = 'fact_table_extract_%s' % year
        c.field = field
        query = app_globals.solr.query('srcid:%s*' % dataset,
                facet='true',
                facet_field=field
                )
        c.facet_counts = query.facet_counts['facet_fields'][c.field]

        c.descriptions = {}
        if field.endswith('code'):
            for k in c.facet_counts:
                entry = model.get_one_entry(k, c.field)
                if entry:
                    c.descriptions[k] = entry.get(c.field.replace('code','description'), '')
        return render('facet/view.html')

    def total(self):
        values = dict(request.params)
        c.values = values
        # if programme_object_code in request.params:
            # undo hack in link creation
        #    po = request.params['po.replace('|', '/')
        #    q += ' programme_object_code:"%s"' % po
        q = ''
        for k,v in values.items():
            q += '%s:"%s" ' % (k,v)
        query = app_globals.solr.query(q, rows=1000, q_op='AND')
        c.results = query.results
        c.count = query.numFound
        if c.count > 5000:
            c.total = 'Too many to count'
        else:
            # put into years
            # exclude net parliamentary funding
            npf_account_code = '31070000'
            c.total = {}
            for hit in query:
                year = hit['dataset'].split('_')[3]
                if hit['account_code'] != npf_account_code:
                    # convert to millions
                    c.total[year] = c.total.get(year, 0) + hit['value'] / 1000.0
                else:
                    c.total['npf'] = c.total['npf'] + hit['value'] / 1000.0
        return render('facet/total.html')

