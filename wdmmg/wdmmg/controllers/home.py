import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

import wdmmg
from wdmmg.lib.base import BaseController, render

log = logging.getLogger(__name__)

class HomeController(BaseController):

    def index(self):
        return 'Where does my money go?: Version %s' % wdmmg.__version__
