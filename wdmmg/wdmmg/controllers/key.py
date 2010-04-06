import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from wdmmg.lib.base import BaseController, render
from wdmmg.lib.helpers import Page
from wdmmg import model

log = logging.getLogger(__name__)

class KeyController(BaseController):

    def view(self, id_=None):
        c.row = (model.Session.query(model.Key)
            .filter_by(id=id_)
            ).one()
        c.num_accounts = (model.Session.query(model.KeyValue)
            .filter_by(key=c.row)
            .filter_by(ns=u'account')
            ).count()
        query = model.Session.query(model.EnumerationValue).filter_by(key_id=c.row.id)
        c.page = Page(
            collection=query,
            page=int(request.params.get('page', 1)),
            items_per_page=c.items_per_page,
            item_count=query.count()
        )
        return render('key/view.html')

    def accounts(self, id_=None):
        c.row = (model.Session.query(model.Key)
            .filter_by(id=id_)
            ).one()
        query = (model.Session.query(model.Account)
            .join((model.KeyValue, model.Account.id==model.KeyValue.object_id))
            .filter_by(key=c.row)
            .order_by(model.Account.id))
        c.page = Page(
            collection=query,
            page=int(request.params.get('page', 1)),
            items_per_page=c.items_per_page,
            item_count=query.count()
        )
        return render('key/accounts.html')

