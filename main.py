from rdflib import Graph, URIRef, Literal

g = Graph()  # Initial empty Graph object

ontology_file_path = "ontology/WhatToMake_Individuals.rdf"
g.parse(ontology_file_path)

query = """
PREFIX food: <http://purl.org/heals/food/>
PREFIX ingredient: <http://purl.org/heals/ingredient/>
SELECT DISTINCT ?recipe
WHERE {
?recipe food:hasIngredient ingredient:Beef .
}
"""

results = g.query(query)

for row in results:
    print(row)
