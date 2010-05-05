import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from wdmmg.lib.base import BaseController, render
from wdmmg.lib.helpers import Page
from wdmmg import model

log = logging.getLogger(__name__)

class KeyController(BaseController):

    def index(self):
        all_keys = model.Session.query(model.Key).all()
        # Make ourselves an index of keys by name.
        c.by_name = {} # name -> Key
        for key in all_keys:
            c.by_name[key.name] = key
        parent_key = self.get_by_name_or_id(model.Key, name_or_id=u'parent')
        # Identify keys with/without parents.
        c.parents = {} # name -> name
        c.by_parent = {} # name -> list of names
        for key in all_keys:
            if parent_key in key.keyvalues:
                c.parents[key.name] = key.keyvalues[parent_key]
            else:
                c.by_parent[key.name] = []
        # For each key that has a parent, attach it to its ultimate ancestor.
        for name in c.parents:
            parent = c.parents[name]
            while parent in c.parents:
                parent = c.parents[parent]
            c.by_parent[parent].append(name)
        return render('key/index.html')

    def view(self, name_or_id=None):
        c.row = self.get_by_name_or_id(model.Key, name_or_id)
        c.num_accounts = (model.Session.query(model.KeyValue)
            .filter_by(key=c.row)
            .filter_by(ns=u'account')
            ).count()
        c.num_enumeration_values = (model.Session.query(model.KeyValue)
            .filter_by(key=c.row)
            .filter_by(ns=u'enumeration_value')
            ).count()
        query = model.Session.query(model.EnumerationValue).filter_by(key_id=c.row.id)
        c.page = Page(
            collection=query,
            page=int(request.params.get('page', 1)),
            items_per_page=c.items_per_page,
            item_count=query.count()
        )
        return render('key/view.html')

    def accounts(self, name_or_id=None):
        c.row = self.get_by_name_or_id(model.Key, name_or_id)
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

