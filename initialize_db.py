import pandas as pd
from rdflib import Graph
from rdflib import URIRef

def initialize_basedOnOntology():
	g = Graph()
	g.parse("tcc_onto_rdf_xml.owl")

	baseURI = 'http://www.semanticweb.org/nicolas/ontologies/2017/3/ontologia-tcc'
	aClass = URIRef(baseURI + '#pessoas')
	rdftype = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")

	pessoas_URIs = []
	nomes = []

	for s,j,o in g.triples((None,rdftype,aClass)):
	    pessoas_URIs.append(s)
	    
	for pessoa in pessoas_URIs:
	    for s,j,o in g.triples((pessoa, URIRef(baseURI+'#hasName'), None)):
	        nomes.append(str(o).lower())

	columns = ['URI', 'Nome completo', 'Primeiro nome', 'Sobrenome']
	pessoasDF = pd.DataFrame(columns=columns)

	pessoasDF['URI'] = pessoas_URIs
	pessoasDF['Nome completo'] = nomes
	pessoasDF['Primeiro nome'] = [p.split(' ')[0].lower() for p in nomes]
	pessoasDF['Sobrenome'] = [p.split(' ')[1].lower() for p in nomes]

	return pessoasDF