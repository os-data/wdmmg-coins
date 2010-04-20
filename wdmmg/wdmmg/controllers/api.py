import logging
from datetime import datetime

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify

from wdmmg.lib.base import BaseController, render

import wdmmg.model as model
import wdmmg.lib.aggregator as aggregator

log = logging.getLogger(__name__)

class ApiController(BaseController):
#    @classmethod
#    def to_datetime(self, s):
#        '''
#        Parses `s` as a date in the format yyyy-mm-dd, and returns it as a 
#        datetime. If `s` is `None`, does not attempt to parse it, but instead
#        returns `None`.
#        '''
#        if not s: return s
#        return datetime.strptime(s, '%Y-%m-%d') # FIXME: Nicer error message needed.

    def index(self):
        # Construct query string by hand to keep the parameters in an instructive order.
        c.aggregate_url = url(controller='api', action='aggregate') + \
        '?slice=cra&exclude-spender=yes&include-cofog1=07&breakdown-dept=yes&breakdown-region=yes&start_date=2004-05&end_date=2004-05'
        # FIXME: Dates are now unicode strings.
        return render('home/api.html')

    @jsonify
    def aggregate(self):
        slice_ = (model.Session.query(model.Slice)
            .filter_by(name=request.params.get('slice'))
            ).one() # FIXME: Nicer error message needed.
        # FIXME: Dates are unicode strings.
        start_date = unicode(request.params.get('start_date', '1000'))
        end_date = unicode(request.params.get('end_date', '3000'))
        # Retrieve request parameters of the form "verb-key=value"
        include, exclude, axes = [], [], []
        for param, value in request.params.items():
            if param.startswith('exclude-'):
                key = (model.Session.query(model.Key)
                    .filter_by(name=unicode(param[8:]))
                    ).one() # FIXME: Nicer error message needed.
                exclude.append((key, value))
            elif param.startswith('include-'):
                key = (model.Session.query(model.Key)
                    .filter_by(name=unicode(param[8:]))
                    ).one() # FIXME: Nicer error message needed.
                include.append((key, value))
            elif param.startswith('breakdown-'):
                key = (model.Session.query(model.Key)
                    .filter_by(name=unicode(param[10:]))
                    ).one() # FIXME: Nicer error message needed.
                axes.append(key) # Value ignored (e.g. "yes").
            # TODO: Other verbs: "per", ...
            elif param in ('slice', 'start_date', 'end_date'):
                pass # Already processed.
            else:
                abort(status_code=400, detail='Unknown request parameter: %s'%param)
#        print slice_
#        print exclude
#        print include
#        print axes
#        print start_date
#        print end_date
        dates, axes, matrix = aggregator.aggregate(
            slice_,
            exclude,
            include,
            axes,
            start_date,
            end_date
        )
        return {
            'metadata': {
                'slice': slice_.name,
                'exclude': [(k.name, v) for (k, v) in exclude],
                'include': [(k.name, v) for (k, v) in include],
                'dates': [unicode(d) for d in dates],
                'axes': axes,
            },
            'results': matrix,
        }

