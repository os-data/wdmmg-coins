import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from wdmmg.lib.base import BaseController, render

from wdmmg import model

log = logging.getLogger(__name__)

class SliceController(BaseController):

    def index(self):
        c.limit = int(request.params.get('limit', '100')) # TODO: Nicer error message.
        c.results = model.Session.query(model.Slice)[:c.limit]
        return render('slice/index.html')

    def view(self, id=None):
        c.row = (model.Session.query(model.Slice)
            .filter_by(id=id)
            ).one()
        c.num_accounts = (model.Session.query(model.Account)
            .filter_by(slice_=c.row)
            ).count()
        c.num_transactions = (model.Session.query(model.Transaction)
            .filter_by(slice_=c.row)
            ).count()
        return render('slice/view.html')

