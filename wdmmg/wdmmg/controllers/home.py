import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from wdmmg.lib.base import BaseController, render
import wdmmg.model as model

log = logging.getLogger(__name__)

class HomeController(BaseController):

    def index(self):
        c.slice_count = model.Session.query(model.Slice).count()
        c.account_count = model.Session.query(model.Account).count()
        c.transaction_count = model.Session.query(model.Transaction).count()
        c.key_count = model.Session.query(model.Key).count()
        return render('home/index.html')

