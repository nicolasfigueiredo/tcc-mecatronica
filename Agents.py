from dialog_act import *
from Constants import *
from auxfunc import *

import requests, Levenshtein, json

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

	def process_msg(act, dialog_state):
	    dialog_state['participants'] = act.content
	    new_act, agenda = check_slots_filled(dialog_state)
	    return new_act, agenda  

	def process_confirm(act, agenda, dialog_state):
	    if act.content == 'accept':
	        dialog_state['participants'] = agenda.content
	        new_act, agenda = check_slots_filled(dialog_state)
	    else:
	        new_act = dialog_act('ask_participants', 'retry')
	        agenda = dialog_act('inform_participants', None)

	    return new_act, agenda

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