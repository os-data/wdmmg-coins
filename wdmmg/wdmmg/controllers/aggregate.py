import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from wdmmg.lib.base import BaseController, render
from wdmmg.lib import aggregator
import wdmmg.model as model

log = logging.getLogger(__name__)

class AggregateController(BaseController):

    def view(self):
        # Do the filtering and aggregation.
        # TODO: Use request params instead of the hard-wired data.
        slice_cra = self.get_by_name_or_id(model.Slice, name_or_id=u'cra')
        key_spender = self.get_by_name_or_id(model.Key, name_or_id=u'spender')
        key_cofog1 = self.get_by_name_or_id(model.Key, name_or_id=u'cofog1')
        key_cofog2 = self.get_by_name_or_id(model.Key, name_or_id=u'cofog2')
        c.filters = {key_cofog1: u'07', key_cofog2: u'07.1'}
        c.axis = request.params.get('breakdown')
        if c.axis:
            c.axis = self.get_by_name_or_id(model.Key, name_or_id=c.axis)
        c.results = aggregator.aggregate(
            slice_=slice_cra,
            exclude=[(key_spender, u'yes')],
            include=c.filters.items(),
            axes=[c.axis] if c.axis else [],
        )
        # Compute totals.
        c.totals = [0.0 for date in c.results.dates]
        for data in c.results.matrix.values():
            for i, amount in enumerate(data):
                c.totals[i] += amount
        # Get all keys for the breakdown drop-down menu.
        c.bd_keys = model.Session.query(model.Key).all()
        # Omit keys that we're filtering on.
        key_parent = self.get_by_name_or_id(model.Key, name_or_id=u'parent')
        for key in c.filters:
          while True:
            print c.bd_keys
#            c.bd_keys.remove(key)
            if key_parent not in key.keyvalues:
              break
            key = self.get_by_name_or_id(model.Key, key.keyvalues[key_parent])
        # TODO: Omit other keys that are useless. How to define?
        return render('aggregate/view.html')

