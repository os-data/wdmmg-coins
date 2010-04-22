import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from wdmmg.lib.base import BaseController, render

from wdmmg import model

log = logging.getLogger(__name__)

class EnumerationValueController(BaseController):

    def view(self, id_=None):
        c.row = (model.Session.query(model.EnumerationValue)
            .filter_by(id=id_)
            ).one()
        c.key = c.row.key
        return render('enumeration_value/view.html')

