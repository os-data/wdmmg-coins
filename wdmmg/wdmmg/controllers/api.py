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
    @classmethod
    def to_datetime(self, s):
        '''
        Parses `s` as a date in the format yyyy-mm-dd, and returns it as a 
        datetime. If `s` is `None`, does not attempt to parse it, but instead
        returns `None`.
        '''
        if not s: return s
        return datetime.strptime(s, '%Y-%m-%d') # FIXME: Nicer error message needed.

    def index(self):
        response.content_type = 'text/plain'
        return '''\
This controller responds to the following requests:

aggregate
=========

Retrieves a slice, specifying axes of interest. The data will be aggregated 
over all other axes.

Example:

    %(aggregate)s?slice=cra&exclude-spender=yes&include-function=7&breakdown-dept=yes&breakdown-region=yes&start_date=2004-01-01&end_date=2005-01-01

Parameters:

    slice=<value> - the name of the data set to retrieve. In the above example, 'cra'
        is the name of the Country Regional Analysis data set.
    
    exclude-<key>=<value> (optional, repeatable) - omit postings whose <key>
        matches <value> (prefix search). In the above example, this is used to
        exclude postings on the central government account, whose "spender"
        attribute is "yes".
        
    include-<key>=<value> (optional, repeatable) - omit postings whose <key>
        does not match <value> (prefix search). In the above example, this is
        used to examine only accounts whose "function" begins with "7" (meaning
        "Health").
    
    breakdown-<key>=<value> (optional, repeatable) - Makes an axis with <key>
        as its coordinate. <value> is ignored.
    
    start_date (optional, default='1000-01-01') - Tranactions before this date 
        are ignored.
    
    end_date (optional, default='3000-01-01') - Transactions on or after this 
        date are ignored.
''' % {
        'aggregate': url(controller='api', action='aggregate')
    }

    @jsonify
    def aggregate(self):
        slice_ = (model.Session.query(model.Slice)
            .filter_by(name=request.params.get('slice'))
            ).one() # FIXME: Nicer error message needed.
        start_date = ApiController.to_datetime(
            request.params.get('start_date', '1000-01-01'))
        end_date = ApiController.to_datetime(
            request.params.get('end_date', '3000-01-01'))
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
#        print slice_
#        print exclude
#        print include
#        print axes
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
                'dates': dates,
                'axes': axes,
            },
            'results': matrix,
        }

# TODO: Move JSON structure into this controller. Useful code follows...
'''
    return {
        'metadata': {
            'exclude': dict([(key.name, value) for key, value in exclude]),
            'include': dict([(key.name, value) for key, value in exclude]),
            'axes': [key.name for key in breakdown_keys]
            'start_date': 
            'end_date':
        },
        'results': [
            (row['amount'], tuple([row[i] for i, _ in enumerate(axes)]))
            for row in results
        ]
    }
'''
