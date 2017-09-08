from dialog_act import *
from Constants import *
from auxfunc import *
import requests, Levenshtein, json


dialog_state = {'intent': False, 'type': '', 'participants': [], 'place': '', 'date': '', 'time': '', 'finished': False}
agenda_act = dialog_act(None, None) # ato dialogal que esperamos receber no momento

def get_dialog_state():
    return dialog_state


def process_dialog_act(act):

    # Função principal.
    # A implementar: a estrutura geral descrita no TCC do Edson e Lucas
    global agenda_act, dialog_state

    # Processa a msg assumindo que seu conteúdo está certo (após a checagem semântica, a ser implementada) 
    new_act, agenda = process_content(act, agenda_act, dialog_state)
    
    agenda_act = agenda
    print(dialog_state)
    
    if dialog_state['finished'] is True:
        #call_blackboard()
        print('\n\n\n Diálogo completo. \n\n\n')
        pass

    return new_act


def process_content(act, agenda, dialog_state):
    
    # Checa a função do ato dialogal e processa o conteúdo da maneira correspondente
    # Podemos implementar seguindo o modelo dos agentes: nesse caso, cada agente é
    # uma função que processa determinado tipo de msg

    if type(act.function) == list:
        new_act, agenda = process_entities(act, dialog_state)
        return new_act, agenda

    if act.function == 'inform_place':    
        new_act, agenda = process_place(act, agenda, dialog_state)
        return new_act, agenda
    
    if act.function == 'inform_participants':
        new_act, agenda = process_participants(act, dialog_state)
        return new_act, agenda

    if act.function == 'accept_or_refuse':  # checa agenda para ver qual pergunta foi feita
        if agenda.function == 'confirm_place' or agenda.function == 'confirm_place_notondb':
            new_act, agenda = process_place_c(act, agenda, dialog_state)
            return new_act, agenda

        elif agenda.function == 'confirm_all':
            new_act, agenda = process_confirm_all(act, agenda, dialog_state)
            return new_act, agenda

        else:
            # Tratar o erro
            pass

    return dialog_act('', ''), dialog_act('', '')



def process_participants(act, dialog_state):
    dialog_state['participants'] = act.content
    new_act, agenda = check_slots_filled(dialog_state)
    return new_act, agenda  

def process_confirm_all(act, agenda, dialog_state):
    if act.content == 'accept':
        dialog_state['finished'] = True
        agenda = dialog_act(None, None)
        new_act = agenda
        return new_act, agenda

    elif act.content == 'refuse':
        new_act = dialog_act('ask_all', None)
        agenda = dialog_act(None, None)
        return new_act, agenda

    return dialog_act(None, None), dialog_act(None, None)


def process_entities(act, dialog_state):

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

def process_place_c(act, agenda, dialog_state):

    if agenda.function == 'confirm_place' or agenda.function == 'confirm_place_notondb':

        if act.content == 'accept':
            dialog_state['place'] = agenda.content
            new_act, agenda = check_slots_filled(dialog_state)
            return new_act, agenda

        elif act.content == 'refuse':
            new_act = dialog_act('ask_place', None)
            agenda = dialog_act(None, None)
            return new_act, agenda

    else:
        return dialog_act(None, None), dialog_act(None, None) 


def process_place(act, agenda, dialog_state):
    
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
        new_act = dialog_act('confirm_specifications', None)
        agenda = dialog_act('confirm_all', None)
        return new_act,agenda