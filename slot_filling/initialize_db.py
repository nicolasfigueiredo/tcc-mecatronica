import pandas as pd
from rdflib import Graph
from rdflib import URIRef

def initialize_peopleDB(path, username):
    # g = Graph()
    # g.parse("./slot_filling/tcc_onto_rdf_xml_2.owl")

    # username = 'nicolas'
    # usernameURI = URIRef('http://www.semanticweb.org/nicolas/ontologies/2017/3/ontologia-tcc#' + username)

    # baseURI = 'http://www.semanticweb.org/nicolas/ontologies/2017/3/ontologia-tcc'
    # aClass = URIRef(baseURI + '#pessoas')
    # rdftype = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")

    # pessoas_URIs = []
    # nomes = []
    # IDs = []

    # for s,j,o in g.triples((None,rdftype,aClass)):
    #     pessoas_URIs.append(s)
        
    # for pessoa in pessoas_URIs:
    #     for s,j,o in g.triples((pessoa, URIRef(baseURI+'#hasName'), None)):
    #         nomes.append(str(o).lower())
    #     for s,j,o in g.triples((pessoa, URIRef(baseURI+'#hasUserID'), None)):
    #         IDs.append(int(o))

    # columns = ['URI', 'Nome completo', 'Primeiro nome', 'Sobrenome', 'Relacao', 'ID']
    # pessoasDF = pd.DataFrame(columns=columns)

    # pessoasDF['URI'] = pessoas_URIs
    # pessoasDF['Nome completo'] = nomes
    # pessoasDF['ID'] = IDs
    # pessoasDF['Primeiro nome'] = [p.split(' ')[0].lower() for p in nomes]
    # pessoasDF['Sobrenome'] = [p.split(' ')[1].lower() for p in nomes]

    # for s,j,o in g.triples((None,None,usernameURI)):
    #     pessoasDF.loc[pessoasDF.loc[:,'URI'] == URIRef(str(s)), 'Relacao'] = str(j).split('#')[1]

    g = Graph()
    g.parse(path)

    usernameURI = URIRef('http://www.semanticweb.org/nicolas/ontologies/2017/3/ontologia-tcc#' + username)

    baseURI = 'http://www.semanticweb.org/nicolas/ontologies/2017/3/ontologia-tcc'
    aClass = URIRef(baseURI + '#pessoas')
    rdftype = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")

    pessoas_URIs = []
    nomes = []
    IDs = []

    for s,j,o in g.triples((None,rdftype,aClass)):
        pessoas_URIs.append(s)
        
    for pessoa in pessoas_URIs:
        for s,j,o in g.triples((pessoa, URIRef(baseURI+'#hasName'), None)):
            nomes.append(str(o).lower())
        for s,j,o in g.triples((pessoa, URIRef(baseURI+'#hasUserID'), None)):
            IDs.append(int(o))

    columns = ['URI', 'Nome completo', 'Primeiro nome', 'Sobrenome', 'Relacao', 'ID']
    pessoasDF = pd.DataFrame(columns=columns)

    pessoasDF['URI'] = pessoas_URIs
    pessoasDF['Nome completo'] = nomes
    pessoasDF['ID'] = IDs
    pessoasDF['Primeiro nome'] = [p.split(' ')[0].lower() for p in nomes]
    pessoasDF['Sobrenome'] = [p.split(' ')[1].lower() for p in nomes]

    for s,j,o in g.triples((None,None,usernameURI)):
        pessoasDF.loc[pessoasDF.loc[:,'URI'] == URIRef(str(s)), 'Relacao'] = str(j).split('#')[1]

    return pessoasDF