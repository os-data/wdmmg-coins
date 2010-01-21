import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons import config

from rdflib.graph import Graph
from semantic.lib.base import BaseController, render

store = config['triplestore']
log = logging.getLogger(__name__)

class GraphController(BaseController):

    def index(self):
        ### kludge for slightly unsafe py4s bindings
	if "cursor" not in config:
		store.connect()
		cursor = store.cursor()
		config["cursor"] = cursor
	else:
		cursor = config["cursor"]

	q = "SELECT ?s ?p ?o WHERE { graph <%s> { ?s ?p ?o } } ORDER BY ?s ?p" % (config["rdf_root"] + request.path,)
	log.info("QUERY: %s" % q)
	accept = request.accept.best_match(["application/rdf+xml", "text/html"])
	if accept == "application/rdf+xml":
        	g = Graph()
		for r in store.query(q):
			g.add(r)
		data = g.serialize()
	else:
		c.cursor = cursor
		c.triples = list(store.query(q))
		data = render("graph.mako")
	cursor.query_state.flush()
	return data
