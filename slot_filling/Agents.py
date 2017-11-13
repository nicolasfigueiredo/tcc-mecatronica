from dialog_act import *
from Constants import *
from auxfunc import *
from initialize_db import *

import requests, json, Levenshtein
import pandas as pd
import gd

nomes_db = 0

def agent_startup(onthology_path, onthology_user_ref):
    global nomes_db
    nomes_db = initialize_peopleDB(onthology_path, onthology_user_ref)
    print(nomes_db.head())

class Agent_Place:

    def process_msg(act, agenda, dialog_state):
        
        # Processa uma mensagem do usuário quando estamos esperando o nome do local do compromisso.
        #
        # Fazemos uma busca no Places API por um local com tal nome. Comparamos o nome
        # do primeiro local obtido com o dado pelo usuário por meio da distância de Leveinshtein, que retorna um índice de 
        # similaridade entre duas strings. 
        
        nomeDado = act.content
        if type(act.content) is list:
            nomeDado = act.content[0]


        # Formatando a URL para o request à Places API
        base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        if dialog_state['type']:
            parameters = {'query': nomeDado, 'location': SAOPAULO, 'radius': '5000', 'type': translate_type[dialog_state['type']], 'key': API_KEY}
        else:
            parameters = {'query': nomeDado, 'location': SAOPAULO, 'radius': '5000', 'key': API_KEY}
        request_url = format_url(base_url, parameters)

        # Recebendo a resposta da API
        r = requests.get(request_url)
        response = r.json()

        print("\n\nResposta do Places API:\n")
        print(response)

        # Checar o que veio na resposta, e, se houve algum resultado, checar a similaridade entre o nome do estabelecimento achado e o dado
        if response['status'] == 'OK':
            nomeAchado = response['results'][0]['name']
            enderecoAchado = response['results'][0]['formatted_address']
            
            # Índice de diferença entre duas strings: quanto menor, mais parecidas as duas palavras
            stringDistance = float(Levenshtein.distance(nomeDado, nomeAchado)) / len(nomeDado)

            if stringDistance < 0.4:
                #dialog_state['place'] = nomeAchado
                new_act = dialog_act('confirm_place', [nomeAchado, format_address(enderecoAchado)])
                agenda = dialog_act('confirm_place', nomeAchado)
                return new_act, agenda

            # No else, para que estado transitar? Algum que aceita um nome sem ele estar no Places API? Implementar
            else:
                new_act = dialog_act('confirm_place_notondb', nomeDado)
                agenda = dialog_act('confirm_place_notondb', nomeDado)
                return new_act, agenda

        elif response['status'] == 'ZERO_RESULTS':
            #dialog_state['place'] = nomeDado
            new_act = dialog_act('confirm_place_notondb', nomeDado)
            agenda = dialog_act('confirm_place_notondb', nomeDado)
            return new_act, agenda

        return dialog_act(None, None), agenda

    def process_confirm(act, agenda, dialog_state):

        if agenda.function == 'confirm_place' or agenda.function == 'confirm_place_notondb':

            if act.content == 'accept':
                dialog_state['place'] = agenda.content
                new_act = dialog_act('', None)
                agenda = dialog_act('', None)
                return new_act, agenda

            elif act.content == 'refuse':
                new_act = dialog_act('ask_place', None)
                agenda = dialog_act('inform_place', None)
                return new_act, agenda

        else:
            return dialog_act(None, None), dialog_act(None, None)

    def format_address(address):
        return ','.join(address.split('-')[:2])


class Agent_Entities:

    def process_msg(act, dialog_state):

        if act.function == 'inform_intent':
            dialog_state['intent'] = act.content
        if act.function == 'inform_type':
            dialog_state['type'] = act.content[0]
        if act.function == 'inform_date':
            dialog_state['date'] = act.content
        if act.function == 'inform_time':
            time = act.content.split(':')[0] + ':' + act.content.split(':')[1]
            dialog_state['time'] = time

def get_candidates(names_db, name):
    candidates = []
    flag = True
    names_given = [x for x in name.split(' ') if len(x) > 1]
        
    for i in range(len(names_db)):
        poss_candidate = names_db.iloc[i]
        poss_candidate_names = poss_candidate['Nome completo'].split(' ')
        for partial_name in names_given:
            if partial_name not in poss_candidate_names:
                flag = False
        if flag:
            candidates.append(poss_candidate)

        flag = True

    return pd.DataFrame(candidates)

class Agent_Participants:

    participantes_a_confirmar = []
    ambiguidades = []
    participantes_sem_ontologia = []
    participantes_confirmados = []

    def process_msg_relationship(act, dialog_state):

        content = act.content
        if type(content) is list:
            content = content[0]
        relationship = translate_relationship(content)

        if len(nomes_db.loc[nomes_db.loc[:,'Relacao'] == relationship]) == 1: # se há alguém com esse tipo de relacionamento na DB
            new_act = dialog_act('confirm_full_name', nomes_db.loc[nomes_db.loc[:,'Relacao'] == relationship, 'Nome completo'].iloc[0])
            agenda = new_act
            return new_act, agenda

        # else: nao conhecemos essa relacao
        new_act = dialog_act('retry_relationship', relationship)
        agenda = dialog_act('inform_participants', None)
        return new_act, agenda
 

    def process_msg(act, dialog_state):

        # Ao receber uma lista de participantes:
        #
        # 1 - Checar se há uma correspondencia única na ontologia. Trẽs casos:
        #       a - Há uma correspondência única
        #       b - A informação é ambígua (ex: usuário disse 'maria', há duas 'marias' na ontologia)
        #       c - A informação procurada não consta de maneira alguma na ontologia
        #
        # 2 - Se houver, resolver ambiguidades (perguntar pro usuário)
        # 3 - Avisar que participantes que não estão na ontologia não participarão da negociação


        if type(act.content) is not list:
            act.content = [act.content]

        for name in act.content:

            candidates = get_candidates(nomes_db, name)

            # Correspondencia única
            if len(candidates) == 1:
                Agent_Participants.participantes_a_confirmar.append(candidates.iloc[0]['Nome completo'])
            # Ambiguidade
            elif len(candidates) > 1:
                Agent_Participants.ambiguidades.append(list(candidates['Nome completo']))
            # Else nome nao está na DB
            else:
                Agent_Participants.participantes_sem_ontologia.append(name)



        new_act, agenda = Agent_Participants.check_lists_participants()
        
        if new_act:
            return new_act, agenda  
    
        new_act = dialog_act('', None)
        agenda = dialog_act('', None)
        return new_act, agenda

    def process_confirm(act, agenda, dialog_state):
        if agenda.function == 'confirm_participants':
            if act.content == 'accept':
                new_act, agenda = process_msg(act, dialog_state)
            else:
                new_act = dialog_act('ask_participants', 'retry')
                agenda = dialog_act('inform_participants', None)

            return new_act, agenda

        if agenda.function == 'confirm_full_name' or agenda.function == 'confirm_participants_notondb':
            if act.content == 'accept':
                if type(agenda.content) is list:
                    dialog_state['participants'] = dialog_state['participants'] + agenda.content 
                else:
                    dialog_state['participants'].append(agenda.content)
                new_act, agenda = Agent_Participants.check_lists_participants()
                if new_act:
                    return new_act, agenda
                new_act = dialog_act('', None)
                agenda = dialog_act('', None)
                return new_act, agenda
            else:
                new_act, agenda = Agent_Participants.check_lists_participants()
                if new_act:
                    return new_act, agenda
                new_act = dialog_act('', None)
                agenda = dialog_act('', None)
                return new_act, agenda

    def resolve_ambiguity(act, agenda, dialog_state):
        if type(act.content) is list:
            content = ' '.join(act.content)
        else:
            content = act.content

        possible_names = agenda.content
        given_names = [x for x in content.split(' ') if len(x)>1]

        candidates = []
        flag = True
        
        for poss_name in possible_names:
            poss_candidate_names = poss_name.split(' ')
            for partial_name in given_names:
                if partial_name not in poss_candidate_names:
                    flag = False
            if flag:
                candidates.append(poss_name)

            flag = True

        if len(candidates) == 1:
            dialog_state['participants'].append(candidates[0])
            new_act, agenda = Agent_Participants.check_lists_participants()
            if new_act:
                return new_act, agenda
            new_act = dialog_act('', None)
            agenda = dialog_act('', None)
            return new_act, agenda

        elif len(candidates) > 1:
            new_act = dialog_act('resolve_ambiguity', candidates)
            agenda = dialog_act('resolve_ambiguity', candidates)
            return new_act, agenda

        # if len(nomes_dados) == 2:
        #     nome_dado = ' '.join(nomes_dados)
        #     for nome in nomes_possiveis:
        #         if nome == nome_dado:
        #             dialog_state['participants'].append(nome)
        #             new_act, agenda = Agent_Participants.check_lists_participants()
        #             if new_act:
        #                 return new_act, agenda
        #             new_act = dialog_act('', None)
        #             agenda = dialog_act('', None)
        #             return new_act, agenda
        # if len(nomes_dados) == 1:
        #     nome_dado = nomes_dados[0]
        #     for nome_possivel in nomes_possiveis:
        #         if nome_dado in nome_possivel: # nome dado faz parte de um nome possivel, ou seja, é sobrenome ou primeiro nome
        #             dialog_state['participants'].append(nome_possivel)
        #             new_act, agenda = Agent_Participants.check_lists_participants()
        #             if new_act:
        #                 return new_act, agenda
        #             new_act = dialog_act('', None)
        #             agenda = dialog_act('', None)
        #             return new_act, agenda

        # else: nome dado não está na DB, checar se isso é ok
        new_act = dialog_act('confirm_participants_notondb', nome_dado)
        agenda = new_act
        return new_act, agenda

    def check_lists_participants():
        if len(Agent_Participants.ambiguidades) > 0:
            amb = Agent_Participants.ambiguidades.pop()
            new_act = dialog_act('resolve_ambiguity', amb)
            agenda = new_act
            return new_act, agenda
        if len(Agent_Participants.participantes_a_confirmar) > 0:
            participante = Agent_Participants.participantes_a_confirmar.pop()
            new_act = dialog_act('confirm_full_name', participante)
            agenda = new_act
            return new_act, agenda
        if len(Agent_Participants.participantes_sem_ontologia) > 0:
            new_act = dialog_act('confirm_participants_notondb', Agent_Participants.participantes_sem_ontologia)
            agenda = new_act
            Agent_Participants.participantes_sem_ontologia = []
            return new_act, agenda

        return None, None