from py4s import FourStore
from rdflib.namespace import Namespace, RDF, RDFS
from rdflib.term import URIRef, Literal, BNode
from rdflib.graph import Graph

XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
DC=Namespace("http://purl.org/dc/terms/")
SCV=Namespace("http://purl.org/NET/scovo#")
DOAP=Namespace("http://usefulinc.com/ns/doap#")
FOAF=Namespace("http://xmlns.com/foaf/0.1/")
OWL=Namespace("http://www.w3.org/2002/07/owl#")
SKOS=Namespace("http://www.w3.org/2004/02/skos/core#")

initNs = { "dc": DC, "rdf" : RDF, "rdfs": RDFS, "scv" : SCV, "doap" : DOAP }

def packages(cursor):
	q = "SELECT DISTINCT ?pkg WHERE { ?pkg a scv:Dataset }"
	g = Graph(identifier="http://semantic.ckan.net/packages")
	for pkg, in cursor.execute(q, initNs=initNs, soft_limit=-1):
		print pkg
		g.add((pkg, RDF.type, SCV["Dataset"]))
	cursor.delete_model(g.identifier)
	cursor.add_model(g)

def tags(cursor):
	q = "SELECT DISTINCT ?tag WHERE { ?s doap:category ?tag }"
	g = Graph(identifier="http://semantic.ckan.net/tags")
	for tag, in cursor.execute(q, initNs=initNs, soft_limit=-1):
		print tag
		g.add((tag, RDF.type, SKOS["Concept"]))
		g2 = Graph(identifier=str(tag))
		g2.add((tag, RDF.type, SKOS["Concept"]))
		g2.add((tag, RDFS.label, Literal(str(tag).split("/")[-1])))
		q = "SELECT DISTINCT ?pkg WHERE { ?pkg doap:category %s }" % tag.n3()
		for pkg, in cursor.execute(q, initNs=initNs, soft_limit=-1):
			g2.add((tag, SCV["dataset"], pkg))
		cursor.delete_model(g2.identifier)
		cursor.add_model(g2)
	cursor.delete_model(g.identifier)
	cursor.add_model(g)
	return g

if __name__ == '__main__':
	store = FourStore("ckan")
	store.connect()
	cursor = store.cursor()

	packages(cursor)
	tags(cursor)
