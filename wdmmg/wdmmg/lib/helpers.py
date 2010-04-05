# -*- coding: utf8 -*-
"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
from webhelpers.html import escape, HTML, literal, url_escape
from webhelpers.html.tags import *
from webhelpers import paginate

class Page(paginate.Page):
    '''Follow ckan setup.'''

    # Curry the pager method of the webhelpers.paginate.Page class, so we have
    # our custom layout set as default.
    def pager(self, *args, **kwargs):
        kwargs.update(
            format="<div class='pager'>$link_previous ~2~ $link_next</div>",
            symbol_previous='« Prev', symbol_next='Next »'
        )
        return super(Page, self).pager(*args, **kwargs)
