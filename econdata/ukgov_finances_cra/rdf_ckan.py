from py4s import FourStore
from rdflib.namespace import Namespace, RDF, RDFS
from rdflib.term import URIRef, Literal
from rdflib.graph import Graph

cra = URIRef("http://ckan.net/package/ukgov-finances-cra")

XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
CRA=Namespace("http://semantic.ckan.net/schema/ukgov-finances-cra#")
DC=Namespace("http://purl.org/dc/terms/")
SCV=Namespace("http://purl.org/NET/scovo#")
initNs = { "cra": CRA, "dc": DC, "rdf" : RDF, "rdfs": RDFS, "scv" : SCV }


def describe(pkgname):
	ckan.package_entity_get(package_name=pkgname)
	pkg = ckan.last_message
	print pkg
	g = Graph(identifier="http://semantic.ckan.net/data/%s" % pkgname)
	s = URIRef("http://ckan.net/package/%s" % pkgname)
	g.add((s, RDF.type, SCV["Dataset"]))
	g.add((s, RDFS.label, Literal(pkg["title"])))
	g.add((s, DC["title"], Literal(pkg["title"])))
	return g

if __name__ == '__main__':
	store = FourStore("ckan")
	store.connect()
	cursor = store.cursor()

	from sys import argv
	import ckanclient
	ckan = ckanclient.CkanClient(api_key=argv[1])

	g = describe('ukgov-finances-cra')
	print g.identifier
	cursor.delete_model(g.identifier)
	cursor.add_model(g)
