import logging
from datetime import datetime

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify
from pylons.decorators.cache import beaker_cache

from wdmmg.lib.base import BaseController, render

import wdmmg.model as model
import wdmmg.lib.aggregator as aggregator
import wdmmg.lib.calculator as calculator

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
        c.rest_url = url(controller='rest', action='index')
        # Construct query strings by hand to keep the parameters in an instructive order.
        c.aggregate_url = url(controller='api', action='aggregate') + \
            '?slice=cra&exclude-spender=yes&include-cofog1=07&breakdown-dept=yes&breakdown-region=yes&start_date=2004-05&end_date=2004-05'
        c.tax_share_url = url(controller='api', action='tax_share') + \
            '?income=20000&spending=10000&smoker=yes&driver=yes'
        return render('home/api.html')

    @beaker_cache(expire=86400, type='dbm', query_args=True)
    @jsonify
    def aggregate(self):
        slice_ = self.get_by_name_or_id(model.Slice,
            name_or_id=request.params.get('slice'))
        start_date = unicode(request.params.get('start_date', '1000'))
        end_date = unicode(request.params.get('end_date', '3000'))
        # Retrieve request parameters of the form "verb-key=value"
        include, exclude, axes, per, per_time = [], [], [], [], []
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
            elif param.startswith('per-'):
                if value:
                    statistic = (model.Session.query(model.Key)
                        .filter_by(name=unicode(param[4:]))
                        ).one() # FIXME: Nicer error message needed.
                    axis = (model.Session.query(model.Key)
                        .filter_by(name=unicode(value))
                        ).one() # FIXME: Nicer error message needed.
                    per.append((axis, statistic))
                else:
                    name = param[4:]
                    assert name in aggregator.time_series, value # FIXME: Nicer error message needed.
                    per_time.append(name)
            # TODO: Other verbs?
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
        results = aggregator.aggregate(
            slice_,
            exclude,
            include,
            axes,
            start_date,
            end_date
        )
        for axis, statistic in per:
#            print axis, statistic
            results.divide_by_statistic(axis, statistic)
        for statistic_name in per_time:
            results.divide_by_time_statistic(statistic_name)
        ans = {
            'metadata': {
                'slice': slice_.name,
                'exclude': [(k.name, v) for (k, v) in exclude],
                'include': [(k.name, v) for (k, v) in include],
                'dates': [unicode(d) for d in results.dates],
                'axes': results.axes,
                'per': [(a.name, s.name) for a, s in per],
                'per_time': per_time
            },
            'results': results.matrix.items(),
        }
#        print ans
        return ans

    @jsonify
    def tax_share(self):
        def float_param(name, required=False):
            if name not in request.params:
                if required:
                    abort(status_code=400, detail='parameter %s is missing'%name)
                return None
            ans = request.params[name]
            try:
                return float(ans)
            except ValueError:
                abort(status_code=400, detail='%r is not a number'%ans)
        def bool_param(name, required=False):
            if name not in request.params:
                if required:
                    abort(status_code=400, detail='parameter %s is missing'%name)
                return None
            ans = request.params[name].lower()
            if ans=='yes': return True
            elif ans=='no': return False
            else: abort(status_code=400, detail='%r is not %r or %r'%(ans, 'yes', 'no'))
        tax, explanation = calculator.tax_share(
            float_param('income', required=True),
            float_param('spending'),
            bool_param('smoker'),
            bool_param('driver')
        )
        return {'tax': tax, 'explanation': explanation}

