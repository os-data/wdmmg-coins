import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from wdmmg.lib.base import BaseController, render

from wdmmg import model

log = logging.getLogger(__name__)

class AccountController(BaseController):

    def index(self):
        c.limit = int(request.params.get('limit', '100')) # TODO: Nicer error message.
        c.slice_ = (model.Session.query(model.Slice)
            .filter_by(id=request.params.get('slice'))
            ).first()
        if not c.slice_:
            c.slice_ = (model.Session.query(model.Slice)
                .filter_by(name=request.params.get('slice'))
                ).first()
        c.results = (model.Session.query(model.Account)
            .filter_by(slice_=c.slice_)
            )[:c.limit]
        return render('account/index.html')

    def view(self, id=None):
        c.row = (model.Session.query(model.Account)
            .filter_by(id=id)
            ).one()
        return render('account/view.html')

