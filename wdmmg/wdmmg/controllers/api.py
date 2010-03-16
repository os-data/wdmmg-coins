import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

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
        yield '''This controller responds to the following URLs:\n\n'''
        for action, description in [
            ('aggregate', '''Retrieves a slice, specifying axes of interest.''')
        ]:
            yield '%s - %s' % (
                url(controller='api', action=action),
                description)
    
    def aggregate(self):
        if 'slice' not in request.params:
            response.content_type = 'text/plain'
            return '''\
Retrieves a slice, specifying axes of interest. The data will be aggregated 
over all other axes.

Example:

    %s?slice=cra&spender_key=govt&spender_value=yes&breakdown_key1=dept&breakdown_key2=region&start_date=2004-01-01&end_date=2005-01-01

Parameters:

    slice - the name of the data set to retrieve.
    
    spender_key (optional, default='spender') - the key name used to 
        distinguish source accounts from destination accounts. Data is only 
        returned for destination accounts.
    
    spender_value (optional, default='yes') - the value that 'spender_key' 
        adopts for source accounts.
    
    breakdown_key1 - The key name used to define the first axis.
    
    breakdown_key2 - etc.
    
    start_date (optional, default='1000-01-01') - Tranactions before this date 
        are ignored.
    
    end_date (optional, default='3000-01-01') - Transactions on or after this 
        date are ignored.
''' % url('api', 'aggregate')
        slice_ = (model.Session.query(model.Slice)
            .filter_by(name=request.params.get('slice'))
            ).one() # FIXME: Nicer error message needed.
        spender_key = (model.Session.query(model.Key)
#            .filter_by(slice_=slice_)
            .filter_by(name=request.params.get('spender_key', u'spender'))
            ).one() # FIXME: Nicer error message needed.
        spender_value = request.params.get('spender_value', u'yes')
        breakdown_keys = []
        while True:
            n = 1 + len(breakdown_keys)
            bd_key_name = request.params.get('breakdown_key%d' % n)
            if not bd_key_name:
                break
            bd_key = (model.Session.query(model.Key)
                .filter_by(name=bd_key_name)
                ).one() # FIXME: Nicer error message needed.
            breakdown_values.append(bd_key)
        start_date = ApiController.to_datetime(request.params.get('start_date'))
        end_date = ApiController.to_datetime(request.params.get('end_date'))
        return aggregator.aggregate(
            slice_,
            spender_key=spender_key,
            spender_values=set([spender_value]),
            breakdown_keys=breakdown_keys,
            start_date=start_date,
            end_date=end_date
        )

