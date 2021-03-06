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
        expire=8640000, # 100 days.
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

    @beaker_cache(type='dbm', query_args=True,
        invalidate_on_startup=True, # So we can still develop.
        expire=8640000, # 100 days.
    )
    def total(self):
        values = dict(request.params)
        c.values = values
        # if programme_object_code in request.params:
            # undo hack in link creation
        #    po = request.params['po.replace('|', '/')
        #    q += ' programme_object_code:"%s"' % po
        q = ''
        # id for use in e.g. disqus
        c.pageid = ''
        for k in sorted(values.keys()):
            v = values[k]
            q += '%s:"%s" ' % (k,v)
            c.pageid += '%s::%s::' % (k,v)
        # " are not allowed in the pageid
        c.pageid = c.pageid.replace('"', "'")
        c.pageid = c.pageid.replace('&', "amp;")
        c.pageid = c.pageid.replace('<', "lt;")
        query = app_globals.solr.query(q, rows=2000, q_op='AND')
        c.results = query.results
        c.count = query.numFound
        if c.count > 2000:
            return 'Too many entries (%s) to sum' % c.count
        else:
            # put into years
            # exclude net parliamentary funding
            npf_account_code = '31070000'
            c.total = {}
            c.npf = {}
            for hit in query:
                year = hit['dataset'].split('_')[3]
                if hit['account_code'] != npf_account_code:
                    # convert to millions
                    c.total[year] = c.total.get(year, 0) + hit['value'] / 1000.0
                else:
                    c.npf[year] = c.npf.get(year, 0) + hit['value'] / 1000.0
        return render('facet/total.html')

