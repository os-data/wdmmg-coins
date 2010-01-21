from py4s import FourStore, sparqlr
from rdflib.graph import Graph
from rdflib.term import URIRef

def load_namespaces(store, nsdict):
	cursor = store.cursor()
	for identifier in nsdict:
		print identifier
		source = nsdict[identifier]
		if source is None: source = identifier
		g = Graph(identifier=identifier)
		g.parse(source)
		cursor.delete_model(g.identifier)
		cursor.add_model(g)

namespaces = {
	# RDF
	"http://www.w3.org/1999/02/22-rdf-syntax-ns" : None,
	# RDFS
	"http://www.w3.org/2000/01/rdf-schema" : None,
	# OWL
	"http://www.w3.org/2002/07/owl" : None,
	# DC
	"http://purl.org/dc/terms/" : None,
	# FOAF
	"http://xmlns.com/foaf/0.1/" : None,
	# DOAP (charset issues)
	#"http://usefulinc.com/ns/doap" : None,
	# SKOS
#	"http://www.w3.org/2004/02/skos/core" : "http://www.w3.org/TR/skos-reference/skos.rdf",
	# SIOC
#	"http://rdfs.org/sioc/ns" : None,
	# SCOVO
	"http://purl.org/NET/scovo" : "http://www.w3.org/2007/08/pyRdfa/extract?uri=http://purl.org/NET/scovo",
}

if __name__ == '__main__':
	store = FourStore("ckan")
	store.connect()
	load_namespaces(store, namespaces)
