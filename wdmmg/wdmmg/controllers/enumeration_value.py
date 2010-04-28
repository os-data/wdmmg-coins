import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from wdmmg.lib.base import BaseController, render

from wdmmg import model

log = logging.getLogger(__name__)

class EnumerationValueController(BaseController):

    def view(self, id_=None):
        c.row = self.get_by_id(model.EnumerationValue, id_)
        c.key = c.row.key
        return render('enumeration_value/view.html')

