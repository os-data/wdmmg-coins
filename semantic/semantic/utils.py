from pylons import config
from rdflib.term import URIRef
from rdflib.namespace import RDFS
import cgi

import logging
log = logging.getLogger(__name__)

def render_html(u):
	cursor = config["cursor"]
	if not isinstance(u, URIRef):
		return cgi.escape("%s" % u)
	q1 = """SELECT DISTINCT ?l WHERE { %s %s ?l . FILTER( lang(?l) = "EN" ) }""" % \
		(u.n3(), RDFS.label.n3())
	q2 = """SELECT DISTINCT ?l WHERE { %s %s ?l }""" % \
		(u.n3(), RDFS.label.n3())
	r = list(cursor.execute(q1))
	if r:
		label = r[0][0]
	else:
		r = list(cursor.execute(q2))
		if r:
			label = r[0][0]
		else:
			label = str(u)
	return '<a href="%s">%s</a>' % (cgi.escape(u), cgi.escape(label))
