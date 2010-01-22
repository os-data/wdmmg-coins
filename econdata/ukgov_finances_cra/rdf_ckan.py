from py4s import FourStore
from rdflib.namespace import Namespace, RDF, RDFS
from rdflib.term import URIRef, Literal, BNode
from rdflib.graph import Graph

cra = URIRef("http://ckan.net/package/ukgov-finances-cra")

XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
DC=Namespace("http://purl.org/dc/terms/")
CRA=Namespace("http://semantic.ckan.net/schema/ukgov-finances-cra#")
SCV=Namespace("http://purl.org/NET/scovo#")
DOAP=Namespace("http://usefulinc.com/ns/doap#")
FOAF=Namespace("http://xmlns.com/foaf/0.1/")

initNs = { "cra": CRA, "dc": DC, "rdf" : RDF, "rdfs": RDFS, "scv" : SCV }


def describe(pkgname):
	ckan.package_entity_get(package_name=pkgname)
	pkg = ckan.last_message
	if not pkg:
		print "empty package", pkg
		return
#	print pkg
	g = Graph(identifier="http://semantic.ckan.net/data/%s" % pkgname)
	s = URIRef("http://ckan.net/package/%s" % pkgname)
	g.add((s, RDF.type, SCV["Dataset"]))
	g.add((s, RDFS.label, Literal(pkg["title"])))
	g.add((s, DC["title"], Literal(pkg["title"])))
	g.add((s, FOAF["homepage"], URIRef(pkg["url"])))
	if pkg["license"]:
		g.add((s, DC["rights"], Literal(pkg["license"])))
	if pkg["notes"]:
		g.add((s, DC["description"], Literal(pkg["notes"])))
	if pkg["tags"]:
		for t in pkg["tags"]:
			g.add((s, DOAP["category"], URIRef("http://semantic.ckan.net/tags/%s" % t)))
	if pkg["groups"]:
		for t in pkg["groups"]:
			pass
	if pkg["download_url"]:
		g.add((s, DOAP["download-page"], URIRef(pkg["download_url"])))
	if pkg["author"] or pkg["author_email"]:
		author = URIRef(str(s) + "#author")
		g.add((s, DC["creator"], author))
		g.add((s, FOAF["maker"], author))
		g.add((author, RDF.type, FOAF["Person"]))
		alabel = ( (pkg["author"] or "") + " " + (pkg["author_email"] or "") ).strip()
		g.add((author, RDFS.label, Literal(alabel)))
		if pkg["author"]:
			g.add((author, FOAF["name"], Literal(pkg["author"])))
		if pkg["author_email"]:
			g.add((author, FOAF["mbox"], URIRef("mailto:" + pkg["author_email"])))
	if pkg["maintainer"] or pkg["maintainer_email"]:
		maint = URIRef(str(s) + "#maintainer")
		g.add((s, DC["contributor"], maint))
		g.add((s, DOAP["maintainer"], maint))
		g.add((maint, RDF.type, FOAF["Person"]))
		mlabel = ( (pkg["maintainer"] or "") + " " + (pkg["maintainer_email"] or "") ).strip()
		g.add((maint, RDFS.label, Literal(mlabel)))
		if pkg["maintainer"]:
			g.add((maint, FOAF["name"], Literal(pkg["maintainer"])))
		if pkg["maintainer_email"]:
			g.add((maint, FOAF["mbox"], URIRef("mailto:" + pkg["maintainer_email"])))
	return g

if __name__ == '__main__':
	store = FourStore("ckan")
	store.connect()
	cursor = store.cursor()

	from sys import argv, exit
	import ckanclient
	ckan = ckanclient.CkanClient(api_key=argv[1])
	try:
		pkg = argv[2]
	except:
		for pkg in ckan.package_register_get():
			print pkg
		exit(0)
	g = describe(pkg)
	print g.identifier
	cursor.delete_model(g.identifier)
	cursor.add_model(g)
