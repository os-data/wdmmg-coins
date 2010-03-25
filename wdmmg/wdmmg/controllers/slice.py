import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from wdmmg.lib.base import BaseController, render

from wdmmg import model

log = logging.getLogger(__name__)

class SliceController(BaseController):

    def index(self):
        c.count = model.Session.query(model.Slice).count()
        return render('slice/index.html')


