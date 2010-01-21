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

def by_department():
	q = """
	SELECT DISTINCT ?dept ?name WHERE {
		?dept a cra:Department .
		?dept rdfs:label ?name
	}
	"""
	for dept, name in cursor.execute(q, initNs=initNs, soft_limit=-1):
		print name
		q = """
		SELECT DISTINCT ?year, ?amount WHERE {
			?area cra:department %s .
			?exp cra:area ?area .
			?exp a cra:Expenditure .
			?exp dc:date ?year .
			?exp rdf:value ?amount
		}
		""" % dept.n3()
		amounts = {}
		for year, amount in cursor.execute(q, initNs=initNs, soft_limit=-1):
			amounts[year] = amounts.setdefault(year, 0.0) + float(amount)
		g = Graph(identifier=str(dept))
		for year in amounts:
			exp = URIRef("%s#%s" % (dept, year))
			g.add((exp, RDF.type, CRA["Expenditure"]))
			g.add((exp, DC["date"], Literal(year)))
			g.add((exp, RDF.value, Literal(amount, datatype=XSD["float"])))
			g.add((exp, RDFS.label, Literal("%s Expenditure %s" % (name, year))))
			g.add((exp, CRA["department"], dept))
		cursor.add_model(g)

def by_function():
	q = """
	SELECT DISTINCT ?function ?name WHERE {
		?function a cra:Function .
		?function rdfs:label ?name
	}
	"""
	for function, name in cursor.execute(q, initNs=initNs, soft_limit=-1):
		print name
		q = """
		SELECT DISTINCT ?year, ?amount WHERE {
			?area cra:function %s .
			?exp cra:area ?area .
			?exp a cra:Expenditure .
			?exp dc:date ?year .
			?exp rdf:value ?amount
		}
		""" % function.n3()
		amounts = {}
		for year, amount in cursor.execute(q, initNs=initNs, soft_limit=-1):
			amounts[year] = amounts.setdefault(year, 0.0) + float(amount)
		g = Graph(identifier=str(function))
		for year in amounts:
			exp = URIRef("%s#%s" % (function, year))
			g.add((exp, RDF.type, CRA["Expenditure"]))
			g.add((exp, DC["date"], Literal(year)))
			g.add((exp, RDF.value, Literal(amount, datatype=XSD["float"])))
			g.add((exp, RDFS.label, Literal("%s Expenditure %s" % (name, year))))
			g.add((exp, CRA["function"], function))
		cursor.add_model(g)

by_department()
by_function()
