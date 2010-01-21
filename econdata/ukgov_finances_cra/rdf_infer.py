from py4s import FourStore
from rdflib import Namespace, RDF, RDFS, URIRef
from rdflib.Graph import Graph

cra = URIRef("http://ckan.net/package/ukgov-finances-cra")

CRA=Namespace("http://semantic.ckan.net/schema/ukgov-finances-cra#")
DC=Namespace("http://purl.org/dc/terms/")
initNs = { "cra": CRA, "dc": DC }

store = FourStore("ckan")
store.connect()
cursor = store.cursor()

def add_type(t, klass=None):
	g = Graph(identifier="http://semantic.ckan.net/data/ukgov-finances-cra/%s" % t)
	if klass is None: klass = t[0].upper() + t[1:-1]
	for x, in cursor.execute("SELECT DISTINCT ?x WHERE { ?x a %s }" % CRA[klass].n3(), soft_limit=-1):
		g.add((x, RDF.type, CRA[klass]))
	cursor.add_model(g)
	cursor.add((cra, RDFS.seeAlso, URIRef(g.identifier)), model_uri="http://semantic.ckan.net/data/ukgov-finances-cra")
	print "Added", klass

## what function exists for each department?
def add_functions():
	for d, in cursor.execute("SELECT DISTINCT ?d WHERE { ?d a cra:Department }", initNs=initNs, soft_limit=-1):
		g = Graph(identifier=str(d))
		q = """
		SELECT DISTINCT ?f WHERE {
			?a a cra:Area .
			?a cra:department %s .
			?a cra:subfunction ?s .
			?s cra:function ?f
		}
		""" % d.n3()
		for f, in cursor.execute(q, initNs=initNs, soft_limit=-1):
			g.add((d, CRA["hasFunction"], f))
		cursor.add_model(g)
	print "Filled in Functions"

## what subfunctions exist for each function?
def add_subfunctions():
	for f, in cursor.execute("SELECT DISTINCT ?f WHERE { ?f a %s }" % CRA["Function"].n3(), soft_limit=-1):
		q = """
		SELECT DISTINCT ?s WHERE {
			?s a cra:SubFunction .
			?s cra:function %s
		}
		""" % (f.n3(),)
		g = Graph(identifier=str(f))
		for s, in cursor.execute(q, initNs=initNs, soft_limit=-1):
			g.add((f, CRA["hasSubFunction"], s))
		cursor.add_model(g)
	print "Filled in Subfunctions"

def add_regions():
	g = Graph(identifier="http://semantic.ckan.net/data/ukgov-finances-cra")
	for r, in cursor.execute("SELECT DISTINCT ?r WHERE { ?s dc:spatial ?r }", initNs=initNs, soft_limit=-1):
		g.add((cra, DC["spatial"], r))
	cursor.add_model(g)
	print "Filled in Spatial"

def add_areas():
	for s, in cursor.execute("SELECT DISTINCT ?f WHERE { ?f a cra:SubFunction }", initNs=initNs, soft_limit=-1):
		g = Graph(identifier=str(s))
		q = """
		SELECT DISTINCT ?a WHERE {
			?a a cra:Area .
			?a cra:subfunction %s
		}
		""" % s.n3()
		for a, in cursor.execute(q, initNs=initNs, soft_limit=-1):
			g.add((s, CRA["hasArea"], a))
		cursor.add_model(g)
	print "Filled in Areas"

add_type("departments")
add_type("functions")
add_type("subfunctions")
add_functions()
add_subfunctions()
add_regions()
add_areas()
