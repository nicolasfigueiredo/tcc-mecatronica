import sys
sys.path.append("./slot_filling")

import pandas as pd
from rdflib import Graph
from rdflib import URIRef
import slot_filling.main

def check_credentials(user, passwd):
	users = {'userA':'', 'userB':'', 'userC':''}
	if user not in users:
		return False
	if users[user] == passwd:
		return True
	return False

def intialize_main_db():
	# ontologia será user_id.owl, nao precisa guardar na db
	users_dict = {'user_id': [1, 2, 3], 'name':['Joao Silva', 'Maria Prado', 'Joao Neves'],
				 'username': ['userA', 'userB', 'userC'], 'name_on_onthology': ['joaosilva','mariaprado','joaoneves']}
	users_db = pd.DataFrame(users_dict)
	return users_db

def initialize_OnthoDB(path, username):
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

def dialog_state_to_JSON(dialog_state, host_id):
	pass


def main():
	user = input('Username:')
	passwd = input('Password:')
	
	if not check_credentials(user, passwd):
		print('Usuário ou senha não encontrados. Saindo...')
		return -1

	users_db = intialize_main_db()
	print(users_db.head())
	user_record = users_db.query('username == @user')
	print(user_record)

	onthology_path = 'onthologies/' + str(int(user_record['user_id'])) + '.owl' 
	onthology_user_ref = str(user_record['name_on_onthology'])
	# pessoas_db = initialize_OnthoDB(onthology_path, onthology_user_ref)
	# print(pessoas_db.head())

	ans = input("Quer marcar um compromisso? (s/n) ")
	if ans == 's':
		print('\nOK!\n')
		a = slot_filling.main.main(onthology_path, onthology_user_ref)

	print(a)
		


if __name__ == '__main__':
    main()