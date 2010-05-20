import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from wdmmg.lib.base import BaseController, render
from wdmmg.lib.helpers import Page
from wdmmg import model

log = logging.getLogger(__name__)

class SliceController(BaseController):

    def index(self):
        c.limit = int(request.params.get('limit', '100')) # TODO: Nicer error message.
        c.results = model.Session.query(model.Slice)[:c.limit]
        return render('slice/index.html')

    def view(self, name_or_id=None):
        c.row = self.get_by_name_or_id(model.Slice, name_or_id)
        c.num_accounts = (model.Session.query(model.Account)
            .filter_by(slice_=c.row)
            ).count()
        c.num_transactions = (model.Session.query(model.Transaction)
            .filter_by(slice_=c.row)
            ).count()
        return render('slice/view.html')

    def accounts(self, name_or_id=None):
        c.items_per_page = int(request.params.get('items_per_page', 50))
        c.slice_ = self.get_by_name_or_id(model.Slice, name_or_id)
        query = model.Session.query(model.Account).filter_by(slice_=c.slice_).order_by(model.Account.name)
        c.page = Page(
            collection=query,
            page=int(request.params.get('page', 1)),
            items_per_page=c.items_per_page,
            item_count=query.count()
        )
        return render('slice/accounts.html')

    def transactions(self, name_or_id=None):
        c.slice_ = self.get_by_name_or_id(model.Slice, name_or_id)
        query = model.Session.query(model.Transaction).filter_by(slice_=c.slice_)
        c.page = Page(
            collection=query,
            page=int(request.params.get('page', 1)),
            items_per_page=c.items_per_page,
            item_count=query.count()
        )
        return render('slice/transactions.html')

