import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons import config

from semantic.lib.base import BaseController, render

from py4s import FourStoreError

log = logging.getLogger(__name__)

DEFAULT_QUERY = """
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
			try:
				c.results = cursor.execute(c.query)
				c.bindings = c.results.bindings
			except FourStoreError:
				c.error = "Error Executing Query (should give a better message)"
				c.bindings = []
				c.results = []
		else:
			c.query = DEFAULT_QUERY
		return render("sparql.mako")
