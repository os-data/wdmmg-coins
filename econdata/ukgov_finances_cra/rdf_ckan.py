from py4s import FourStore
from rdflib.namespace import Namespace, RDF, RDFS
from rdflib.term import URIRef, Literal
from rdflib.graph import Graph

cra = URIRef("http://ckan.net/package/ukgov-finances-cra")

XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
CRA=Namespace("http://semantic.ckan.net/schema/ukgov-finances-cra#")
DC=Namespace("http://purl.org/dc/terms/")
initNs = { "cra": CRA, "dc": DC, "rdf" : RDF, "rdfs": RDFS }

store = FourStore("ckan")
store.connect()
cursor = store.cursor()

if __name__ == '__main__':
	from sys import argv
	import ckanclient
	ckan = ckanclient.CkanClient(api_key=argv[1])
	ckan.package_entity_get(package_name='ukgov-finances-cra')
	pkg = ckan.last_message
	print pkg
