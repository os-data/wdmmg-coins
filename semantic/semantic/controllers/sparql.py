import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons import config

from semantic.lib.base import BaseController, render

from py4s import FourStoreError

log = logging.getLogger(__name__)

DEFAULT_QUERY = """\
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX cra: <http://semantic.ckan.net/schema/ukgov-finances-cra#>

SELECT DISTINCT ?dept ?year ?amount
WHERE {
	?dept a cra:Department .
	?exp cra:department ?dept .
	?exp a cra:Expenditure .
	?exp dc:date ?year .
	?exp rdf:value ?amount
} 
ORDER BY ?dept ?year
"""

import re
forbidden = re.compile(".*(INSERT|DELETE).*", re.IGNORECASE|re.MULTILINE)

class SparqlController(BaseController):

	def index(self):
		### kludge for slightly unsafe py4s bindings
		store = config["triplestore"]
		if "cursor" not in config:
			store.connect()
			cursor = store.cursor()
			config["cursor"] = cursor
		else:
			cursor = config["cursor"]
		
		c.query = request.POST.get("query", None)
		if c.query:
			if forbidden.match(c.query.replace("\n", " ")):
				c.results = []
				c.bindings = []
				c.warnings = ["Operation Not Allowed"]
			else:
				try:
					results = cursor.execute(c.query)
					c.bindings = results.bindings
					c.results = list(results)
				except FourStoreError:
					c.bindings = []
					c.results = []
				c.warnings = cursor.warnings
		else:
			c.query = DEFAULT_QUERY
		result = render("sparql.mako")
		cursor.flush()
		return result
