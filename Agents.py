from dialog_act import *
from Constants import *
from auxfunc import *
from initialize_db import *

import requests, Levenshtein, json
import pandas as pd

nomes_db = initialize_basedOnOntology()
print(nomes_db.head())

class Agent_Place:

    def process_msg(act, agenda, dialog_state):
        
        # Processa uma mensagem do usuário quando estamos esperando o nome do local do compromisso.
        #
        # Fazemos uma busca no Places API por um local com tal nome. Comparamos o nome
        # do primeiro local obtido com o dado pelo usuário por meio da distância de Leveinshtein, que retorna um índice de 
        # similaridade entre duas strings. 
        
        nomeDado = act.content

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
                new_act = dialog_act('confirm_place', [nomeAchado, enderecoAchado])
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
                new_act, agenda = check_slots_filled(dialog_state)
                return new_act, agenda

            elif act.content == 'refuse':
                new_act = dialog_act('ask_place', None)
                agenda = dialog_act('inform_place', None)
                return new_act, agenda

        else:
            return dialog_act(None, None), dialog_act(None, None)


class Agent_Entities:

    def process_msg(act, dialog_state):

        for function, content in zip(act.function, act.content):
            if function == 'inform_intent':
                dialog_state['intent'] = content
            if function == 'inform_type':
                dialog_state['type'] = content
            if function == 'inform_date':
                dialog_state['date'] = content
            if function == 'inform_time':
                dialog_state['time'] = content
            
        new_act, agenda = check_slots_filled(dialog_state)  # procura quais slots ainda devem ser preenchidos, para fazermos a prox pergunta
        return new_act, agenda


class Agent_Participants:

    participantes_a_confirmar = []
    ambiguidades = []
    participantes_sem_ontologia = []
    participantes_confirmados = []

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
            if len(name.split(' ')) == 1:   # foi informado apenas o primeiro nome ou sobrenome
                if len(nomes_db[nomes_db['Primeiro nome'] == name]) == 1:
                    Agent_Participants.participantes_a_confirmar.append(nomes_db[nomes_db['Primeiro nome'] == name].iloc[0]['Nome completo'])
                elif len(nomes_db[nomes_db['Sobrenome'] == name]) == 1:
                    Agent_Participants.participantes_a_confirmar.append(nomes_db[nomes_db['Sobrenome'] == name].iloc[0]['Nome completo'])
                elif len(nomes_db[nomes_db['Primeiro nome'] == name]) > 1:
                    Agent_Participants.ambiguidades.append(list(nomes_db[nomes_db['Primeiro nome'] == name]['Nome completo']))
                elif len(nomes_db[nomes_db['Sobrenome'] == name]) > 1:
                    Agent_Participants.ambiguidades.append(list(nomes_db[nomes_db['Sobrenome'] == name]['Nome completo']))
                else:
                    Agent_Participants.participantes_sem_ontologia.append(name)

            else:
                if len(nomes_db[nomes_db['Nome completo'] == name]) == 1:
                    Agent_Participants.participantes_confirmados.append(nomes_db[nomes_db['Nome completo'] == name].iloc[0]['Nome completo'])
                else:
                    Agent_Participants.participantes_sem_ontologia.append(name)


        new_act, agenda = Agent_Participants.check_lists_participants()
        
        if new_act:
            return new_act, agenda  
    
        new_act, agenda = check_slots_filled(dialog_state)
        return new_act, agenda  

    def process_confirm(act, agenda, dialog_state):
        if agenda.function == 'confirm_participants':
            if act.content == 'accept':
                dialog_state['participants'] = agenda.content
                new_act, agenda = check_slots_filled(dialog_state)
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
                if not new_act:
                    new_act, agenda = check_slots_filled(dialog_state)
                return new_act, agenda
            else:
                new_act, agenda = Agent_Participants.check_lists_participants()
                if not new_act:
                    new_act, agenda = check_slots_filled(dialog_state)
                return new_act, agenda

    def resolve_ambiguity(act, agenda, dialog_state):
        nome_dado = act.content
        nomes_possiveis = agenda.content

        for nome in nomes_possiveis:
            if nome == nome_dado:
                dialog_state['participants'].append(nome)
                new_act, agenda = Agent_Participants.check_lists_participants()
                if not new_act:
                    new_act, agenda = check_slots_filled(dialog_state)
                return new_act, agenda

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

def check_slots_filled(dialog_state):

        # procura quais slots ainda devem ser preenchidos, e escolhe uma pergunta a ser feita

        if not dialog_state['type']:
            new_act = dialog_act('ask_type', None)
            agenda = dialog_act('inform_type', None)
            return new_act,agenda
        
        elif not dialog_state['participants']:
            new_act = dialog_act('ask_participants', None)
            agenda = dialog_act('inform_participants', None)
            return new_act,agenda
        
        elif not dialog_state['place']:
            new_act = dialog_act('ask_place', None)
            agenda = dialog_act('inform_place', None)
            return new_act,agenda
        
        elif not dialog_state['date']:
            new_act = dialog_act('ask_date', None)
            agenda = dialog_act('inform_date', None)
            return new_act,agenda
        
        elif not dialog_state['time']:
            new_act = dialog_act('ask_time', None)
            agenda = dialog_act('inform_time', None)
            return new_act,agenda
        
        else:
            new_act = dialog_act('confirm_all', None)
            agenda = dialog_act('confirm_all', None)
            return new_act,agenda