import db
import swiss
import logging
from datetime import datetime
from urllib2 import HTTPError

from rdflib.graph import Graph
from rdflib.term import BNode, URIRef, Literal
from rdflib.namespace import Namespace, RDF, RDFS

SITE_ROOT = "http://semantic.ckan.net/"

XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
DC = Namespace("http://purl.org/dc/terms/")
SCV = Namespace("http://purl.org/NET/scovo#")
CRA_SCHEMA_URI = SITE_ROOT + "schema/ukgov-finances-cra"
CRA = Namespace(CRA_SCHEMA_URI + "#")
CRA_DATA_URI = SITE_ROOT + "data/ukgov-finances-cra"
CRA_DATA = Namespace(SITE_ROOT + "data/ukgov-finances-cra/")
cra = URIRef("http://ckan.net/package/ukgov-finances-cra")

_qns = {
	'dc' : DC,
	'scv' : SCV,
	'cra' : CRA
}

## stolen from django
def slugify(value):
	"""
	Normalizes string, converts to lowercase, removes non-alpha characters,
	and converts spaces to hyphens.
	"""
	import unicodedata, re
	value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
	value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
	return re.sub('[-\s]+', '-', value)

def schema():
	## Some schema definitions
	g = Graph(identifier=CRA_SCHEMA_URI)

	g.add((CRA["Area"], RDFS.subClassOf, SCV["Dimension"]))
	g.add((CRA["Area"], RDFS.label, Literal("Area")))
	g.add((CRA["area"], RDF.type, RDF.Property))
	g.add((CRA["area"], RDFS.label, Literal("belongs to area")))
	g.add((CRA["area"], RDFS.domain, CRA["Expenditure"]))
	g.add((CRA["area"], RDFS.range, CRA["Area"]))
	g.add((CRA["hasArea"], RDF.type, RDF.Property))
	g.add((CRA["hasArea"], RDFS.label, Literal("has area")))
	g.add((CRA["hasArea"], RDFS.range, CRA["Area"]))

	g.add((CRA["Department"], RDFS.subClassOf, SCV["Dimension"]))
	g.add((CRA["Department"], RDFS.label, Literal("Department")))
	g.add((CRA["department"], RDF.type, RDF.Property))
	g.add((CRA["department"], RDFS.label, Literal("belongs to department")))
	g.add((CRA["department"], RDFS.domain, CRA["Area"]))
	g.add((CRA["department"], RDFS.range, CRA["Department"]))
	g.add((CRA["hasDepartment"], RDF.type, RDF.Property))
	g.add((CRA["hasDepartment"], RDFS.label, Literal("has department")))
	g.add((CRA["hasDepartment"], RDFS.range, CRA["Department"]))

	g.add((CRA["Function"], RDFS.subClassOf, SCV["Dimension"]))
	g.add((CRA["Function"], RDFS.label, Literal("Function")))
	g.add((CRA["function"], RDF.type, RDF.Property))
	g.add((CRA["function"], RDFS.label, Literal("belongs to function")))
	g.add((CRA["function"], RDFS.domain, CRA["SubFunction"]))
	g.add((CRA["function"], RDFS.range, CRA["Function"]))
	g.add((CRA["hasFunction"], RDF.type, RDF.Property))
	g.add((CRA["hasFunction"], RDFS.label, Literal("has function")))
	g.add((CRA["hasFunction"], RDFS.range, CRA["Function"]))

	g.add((CRA["SubFunction"], RDFS.subClassOf, SCV["Dimension"]))
	g.add((CRA["SubFunction"], RDFS.label, Literal("SubFunction")))
	g.add((CRA["subfunction"], RDF.type, RDF.Property))
	g.add((CRA["subfunction"], RDFS.label, Literal("belongs to subfunction")))
	g.add((CRA["subfunction"], RDFS.domain, CRA["Area"]))
	g.add((CRA["subfunction"], RDFS.range, CRA["SubFunction"]))
	g.add((CRA["hasSubFunction"], RDF.type, RDF.Property))
	g.add((CRA["hasSubFunction"], RDFS.label, Literal("has subfunction")))
	g.add((CRA["hasSubFunction"], RDFS.range, CRA["SubFunction"]))


	g.add((CRA["Expenditure"], RDFS.subClassOf, SCV["Item"]))
	g.add((CRA["Expenditure"], RDFS.label, Literal("Expenditure")))

	return g

def make_area(a):
	slug = "areas/" + slugify(a.region) + "/" + slugify(a.department) + "/" + slugify(a.pog) + "/" + slugify(a.function) + "/" + slugify(a.subfunction)
	g = Graph(identifier=CRA_DATA_URI + "/" + slug)
	area = CRA_DATA[slug]
	g.add((area, RDF.type, CRA["Area"]))
	g.add((area, SCV["dataset"], cra))
	g.add((area, RDFS.label, Literal("%s (%s)" % (a.title, a.region))))
	g.add((area, DC["title"], Literal(a.title)))
	g.add((area, DC["identifier"], Literal(a.pog)))
	if a.notes:
		g.add((area, DC["description"], Literal(a.notes)))

	g.add((area, CRA["department"], CRA_DATA["departments/" + slugify(a.department)]))
	g.add((area, DC["spatial"], Literal(a.region)))

	func = "functions/" + slugify(a.function)
	g.add((area, CRA["function"], CRA_DATA[func]))
	subf = func + "/" + slugify(a.subfunction)
	g.add((area, CRA["subfunction"], CRA_DATA[subf]))

	for e in a.expenditures:
		exp = URIRef("%s#%s" % (area, e.year))
		g.add((exp, RDF.type, CRA["Expenditure"]))
		g.add((exp, RDFS.label, Literal("%s (%s) Expenditure %s" % (a.title, a.region, e.year))))
		g.add((exp, RDF.value, Literal(e.amount, datatype=XSD["float"])))
		g.add((exp, DC["date"], Literal(e.year)))
		g.add((exp, SCV["dataset"], cra))
		g.add((exp, CRA["area"], area))
	return g

def make_department(department, deptcode):
	dept = CRA_DATA["departments/" + slugify(department)]
	g = Graph(identifier="%s" % dept)
	g.add((dept, RDF.type, CRA["Department"]))
	g.add((dept, RDFS.label, Literal(department)))
	g.add((dept, DC["title"], Literal(department)))
	g.add((dept, DC["identifier"], Literal(deptcode)))
	g.add((dept, SCV["dataset"], cra))
	return g

def make_function(function):
	func = CRA_DATA["functions/" + slugify(function)]
	g = Graph(identifier="%s" % func)
	g.add((func, RDF.type, CRA["Function"]))
	g.add((func, RDFS.label, Literal(function)))
	g.add((func, DC["title"], Literal(function)))
	g.add((func, DC["identifier"], Literal(slugify(function))))
	g.add((func, SCV["dataset"], cra))
	return g

def make_subfunction(function, subfunction):
	subf = CRA_DATA["functions/" + slugify(function) + "/" + slugify(subfunction)]
	g = Graph(identifier="%s" % subf)
	g.add((subf, RDF.type, CRA["SubFunction"]))
	g.add((subf, RDFS.label, Literal(subfunction)))
	g.add((subf, DC["title"], Literal(subfunction)))
	g.add((subf, DC["identifier"], Literal(slugify(subfunction))))
	g.add((subf, CRA["function"], CRA_DATA["functions/" + slugify(function)]))
	g.add((subf, SCV["dataset"], cra))
	return g

if __name__ == '__main__':
	cache = swiss.Cache('cache')
	dburi = 'sqlite:///%s' % cache.cache_path('ukgov_finances_cra.db')
	db.Repository(dburi)

	logging.basicConfig(
		level=logging.INFO,
		format = "%(asctime)s - %(name)s:%(levelname)s - %(message)s"
	)
	log = logging.getLogger("cra[rdf]")

	from py4s import FourStore
	store = FourStore("ckan")
	store.connect()
        cursor = store.cursor()

	t0 = datetime.now()

	cursor.delete_model(CRA_SCHEMA_URI)
	cursor.add_model(schema())
        cursor.add((cra, RDF.type, SCV["Dataset"]), CRA_DATA_URI)

	for row in db.Session.execute("SELECT DISTINCT department, deptcode FROM area"):
		g = make_department(*row)
		start = datetime.now()
		cursor.delete_model(g.identifier)
		cursor.add_model(g)
		end = datetime.now()
		print end-start, g.identifier

	for row in db.Session.execute("SELECT DISTINCT function FROM area"):
		g = make_function(*row)
		start = datetime.now()
		cursor.delete_model(g.identifier)
		cursor.add_model(g)
		end = datetime.now()
		print end-start, g.identifier

	for row in db.Session.execute("SELECT DISTINCT function, subfunction FROM area"):
		g = make_subfunction(*row)
		start = datetime.now()
		cursor.delete_model(g.identifier)
		cursor.add_model(g)
		end = datetime.now()
		print end-start, g.identifier

	for a in db.Session.query(db.Area):
		g = make_area(a)
		start = datetime.now()
		cursor.delete_model(g.identifier)
		cursor.add_model(g)
		end = datetime.now()
		print end-start, g.identifier

	t1 = datetime.now()
	log.info("Processed %ss" % (t1-t0))
