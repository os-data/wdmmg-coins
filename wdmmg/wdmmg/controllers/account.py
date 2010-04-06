import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from wdmmg.lib.base import BaseController, render
from wdmmg.lib.helpers import Page
from wdmmg import model

log = logging.getLogger(__name__)

class AccountController(BaseController):

    def view(self, id_=None):
        c.row = (model.Session.query(model.Account)
            .filter_by(id=id_)
            ).one()
        c.num_postings = (model.Session.query(model.Posting)
            .filter_by(account=c.row)
            ).count()
        return render('account/view.html')

    def postings(self, id_=None):
        c.row = (model.Session.query(model.Account)
            .filter_by(id=id_)
            ).one()
        query = (model.Session.query(model.Posting)
            .filter_by(account=c.row)
            .order_by('timestamp'))
        c.page = Page(
            collection=query,
            page=int(request.params.get('page', 1)),
            items_per_page=c.items_per_page,
            item_count=query.count()
        )
        return render('account/postings.html')

