from pylons import config
from rdflib.term import URIRef
from rdflib.namespace import RDFS
import cgi

def render_html(u):
	cursor = config["cursor"]
	if not isinstance(u, URIRef):
		return cgi.escape("%s" % u)
	r = cursor.execute("SELECT DISTINCT ?l WHERE { %s %s ?l }" % (u.n3(), RDFS.label.n3()))
	if r:
		label = list(r)[0][0]
	else:
		label = str(u)
	return '<a href="%s">%s</a>' % (cgi.escape(u), cgi.escape(label))
