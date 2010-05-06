import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from wdmmg.lib.base import BaseController, render
from wdmmg.lib import aggregator
import wdmmg.model as model

log = logging.getLogger(__name__)

class AggregateController(BaseController):
    def view(self):
        # Read request parameters.
        slice_cra = self.get_by_name_or_id(model.Slice,
            name_or_id=request.params.get('slice', u'cra'))
        c.filters = {}
        for param, value in request.params.items():
            if param.startswith('include-'):
                key = self.get_by_name_or_id(model.Key, name_or_id=unicode(param[8:]))
                c.filters[key] = value
        c.axis = request.params.get('breakdown')
        if c.axis:
            c.axis = self.get_by_name_or_id(model.Key, name_or_id=c.axis)
        # TODO: Generalise this hard-wired data:
        key_spender = self.get_by_name_or_id(model.Key, name_or_id=u'spender')
        # Do the aggregation.
        c.results = aggregator.aggregate(
            slice_=slice_cra,
            exclude=[(key_spender, u'yes')],
            include=c.filters.items(),
            axes=[c.axis] if c.axis else [],
        )
        # Function for making small changes to the URL.
        def make_url(add_filter_value=None, remove_filter_key=None):
            new_filters = dict(c.filters)
            new_axis = c.axis
            if add_filter_value:
                new_filters[c.axis] = add_filter_value
                new_axis = None # TODO: Make a better choice.
            if remove_filter_key:
                del new_filters[remove_filter_key]
            params = dict([('include-'+str(key.name), value)
                for key, value in new_filters.items()])
            if new_axis:
                params['breakdown'] = new_axis.name
            return url(controller='aggregate', action='view', **params)
        # Generate info for filters.
        c.filter_labels = dict([(key.name, c.filters[key])
            for key in c.filters])
        c.filter_links = dict([(key.name, make_url(remove_filter_key=key))
            for key in c.filters])
        # Get all Keys for the breakdown drop-down menu.
        c.bd_keys = model.Session.query(model.Key).all()
        # Generate info for breakdown row headings.
        if c.axis:
            c.axis_labels = dict([(ev.code, u'%s: %s' % (ev.code, ev.name))
                for ev in model.Session.query(model.EnumerationValue)
                    .filter_by(key=c.axis).all()])
            c.axis_links = dict([(coordinates[0], make_url(add_filter_value=coordinates[0]))
                for coordinates in c.results.matrix.keys()])
        # Compute totals.
        c.totals = [0.0 for date in c.results.dates]
        for data in c.results.matrix.values():
            for i, amount in enumerate(data):
                c.totals[i] += amount
        # TODO: Omit keys that are useless. How to define?
        return render('aggregate/view.html')

