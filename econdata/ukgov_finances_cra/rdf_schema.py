from py4s import FourStore
from rdflib.graph import Graph

store = FourStore("ckan")
store.connect()
cursor = store.cursor()

# RDF
uri = "http://www.w3.org/1999/02/22-rdf-syntax-ns"
g = Graph(identifier=uri)
g.parse(uri)
cursor.add_model(g)

# RDFS
uri = "http://www.w3.org/2000/01/rdf-schema"
g = Graph(identifier=uri)
g.parse(uri)
cursor.add_model(g)

# DC
uri = "http://purl.org/dc/terms/"
g = Graph(identifier=uri)
g.parse(uri)
cursor.add_model(g)

# SCOVO
uri = "http://www.w3.org/2007/08/pyRdfa/extract?uri=http://purl.org/NET/scovo"
g = Graph(identifier="http://purl.org/NET/scovo")
g.parse(uri)
cursor.add_model(g)
