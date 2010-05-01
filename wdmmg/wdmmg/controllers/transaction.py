import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from wdmmg.lib.base import BaseController, render
from wdmmg.lib.helpers import Page
from wdmmg import model

log = logging.getLogger(__name__)

class TransactionController(BaseController):
    def index(self):
        query = model.Session.query(model.Transaction)
        c.page = Page(
            collection=query,
            page=int(request.params.get('page', 1)),
            items_per_page=c.items_per_page,
            item_count=query.count(),
        )
        return render('transaction/index.html')

    def view(self, id_=None):
        c.row = self.get_by_id(model.Transaction, id_)
        return render('transaction/view.html')

