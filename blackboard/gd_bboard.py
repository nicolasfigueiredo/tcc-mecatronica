import sys
import json

from dialog_act import *
from Constants import *

dialog_state = {}
event = {}
agenda_act = dialog_act(None, None) # ato dialogal que esperamos receber no momento

def startup(json_data):
    # Recebe um JSON descrevendo a tarefa do assistente (ex: apresentar o convite para um evento, 
    # consultar a disponibilidade do usuário em um horário proposto), prepara o dialog_state com as informações
    # que devem ser coletadas e a representação do evento sendo negociado

    global agenda_act, dialog_state, event

    if json_data['task'] == 'accept_invite':
        # dialog_state['task'] = 'accept_invite'
        dialog_state['accept_invite'] = None
        dialog_state['accept_original_time'] = None
        dialog_state['propose_alternate_time'] = None
        dialog_state['alternate_date'] = None
        dialog_state['alternate_time'] = None

        event = json_data['event']
        agenda_act = dialog_act("propose_invite", event) 
        return agenda_act

    if json_data['task'] == 'check_alternate_time':
        # dialog_state['task'] = 'check_alternate_time'
        dialog_state['accept_alternate_time'] = None
        agenda_act = dialog_act('check_alternate_time', json_data)
        return agenda_act

    if json_data['task'] == 'schedule_event':
        # dialog_state['task'] = 'schedule_event'
        event = json_data['event']
        agenda_act = dialog_act('schedule_event', event)
        return agenda_act

    if json_data['task'] == 'authorize_alternate_time':
        dialog_state['authorize_alternate_time'] = None
        dialog_state['present_alt_time'] = None
        agenda_act = dialog_act('authorize_alternate_time', json_data)
        return agenda_act



    if json_data['task'] == 'decide_final_time':
        # dialog_state['task'] = 'check_alternate_time'
        dialog_state['cancel_event'] = None
        dialog_state['final_date'] = None
        dialog_state['final_time'] = None
        if len(json_data['possible_times']) == 1:
            agenda_act = dialog_act('decide_final_time_oneoption', json_data)
        else:
            agenda_act = dialog_act('decide_final_time_multoptions', json_data)
        return agenda_act

def get_dialog_state():
    return dialog_state

def process_dialog_act(acts):

    # Função principal.
    global agenda_act, dialog_state, event

    print("\n\nAgenda:\n")
    agenda_act.print()


    for act in acts:
        if not act.function:
            new_act, agenda = process_error(act, agenda_act, dialog_state)

            # Processa a msg assumindo que seu conteúdo está certo (após a checagem semântica, a ser implementada) 
        else:
            new_act, agenda = process_content(act, agenda_act, dialog_state, event)
            
    agenda_act = agenda
    print("\n\nEstado do diálogo:\n")
    print(dialog_state)
    print("\n\nAgenda:\n")
    agenda.print()
    
    return new_act

def process_error(act, agenda, dialog_state):

    # Recebe um ato dialogal que não foi entendido, checa a agenda para decidir como proceder
    # Dependendo do tipo de expectativa do sistema, prosseguirá de um dos seguintes jeitos:
    # 
    #   1 - Repetirá a pergunta.
    #   2 - Confirma se o que recebeu é a informação que estava esperando (ex: a palavra não entendida é o nome do restaurante)
    #
 
    return agenda, agenda

def process_content(act, agenda, dialog_state, event):
    
    # Checa a função do ato dialogal e processa o conteúdo da maneira correspondente
    # Podemos implementar seguindo o modelo dos agentes: nesse caso, cada agente é
    # uma função que processa determinado tipo de msg

    function = act.function
    content = act.content
    
    if function == 'inform_date':
        if 'alternate_date' in dialog_state:
            dialog_state['propose_alternate_time'] = True
            dialog_state['alternate_date'] = content
        if 'final_date' in dialog_state:
            dialog_state['final_date'] = content
            dialog_state['cancel_event'] = False

        new_act, agenda = check_slots_filled(dialog_state)  # procura quais slots ainda devem ser preenchidos, para fazermos a prox pergunta
        return new_act, agenda


    elif function == 'inform_time':
        if 'final_date' in dialog_state:
            dialog_state['final_time'] = content
            dialog_state['cancel_event'] = False       
        if 'alternate_date' in dialog_state:
            dialog_state['propose_alternate_time'] = True
            dialog_state['alternate_time'] = content
            
        new_act, agenda = check_slots_filled(dialog_state)  # procura quais slots ainda devem ser preenchidos, para fazermos a prox pergunta
        return new_act, agenda



    elif act.function == 'accept_or_refuse':

        if agenda.function == 'schedule_event':
            if act.content == 'accept':
                # TO DO: integração com o Google Calendar
                if True: # substituir por algo que retorna True se conseguiu marcar
                    return dialog_act("schedule_success", ''), dialog_act('','')
                else:
                    return dialog_act("schedule_failure", ''), dialog_act('','')
            if act.content == 'refuse':
                return dialog_act("schedule_not_needed", ''), dialog_act('', '')

        if agenda.function == "check_alternate_time":
            if act.content == 'accept':
                dialog_state['accept_alternate_time'] = True
            elif act.content == 'refuse':
                dialog_state['accept_alternate_time'] = False
            return dialog_act('finish_dialog', ''), dialog_act('','')

        if agenda.function == 'propose_invite':         
            if act.content == 'accept':
                dialog_state['accept_invite'] = True
                return dialog_act('accept_original_time', event), dialog_act('accept_original_time', event)
            elif act.content == 'refuse':
                dialog_state['accept_invite'] = False
                return dialog_act('decline_invite', ''), dialog_act('', '')

        if agenda.function == 'accept_original_time':
            if act.content == 'accept':
                dialog_state['accept_original_time'] = True
            if act.content == 'decline':
                dialog_state['accept_original_time'] = False
            return dialog_act('propose_alternate_time', event), dialog_act('propose_alternate_time', event)

        if agenda.function == 'propose_alternate_time':
            if act.content == 'accept':
                dialog_state['propose_alternate_time'] = True
                return dialog_act('ask_alternate_time', ''), dialog_act('ask_alternate_time', '')
            if act.content == 'refuse':
                dialog_state['propose_alternate_time'] = False
                return dialog_act('finish_dialog', ''), dialog_act('','')

        if agenda.function == 'decide_final_time_oneoption':
            if act.content == 'accept':
                dialog_state['cancel_event'] = False
                dialog_state['final_date'] = agenda.content['possible_times'][0]['date']
                dialog_state['final_time'] = agenda.content['possible_times'][0]['time']
                return dialog_act('finish_dialog', ''), dialog_act('','')
            if act.content == 'refuse':
                return dialog_act('cancel_event', ''), dialog_act('cancel_event', agenda.content)

        if agenda.function == 'cancel_event':
            if act.content == 'accept':
                dialog_state['cancel_event'] = True
                return dialog_act('finish_dialog', ''), dialog_act('','')
            if act.content == 'refuse':
                return dialog_act('decide_final_time_oneoption', agenda.content), dialog_act('decide_final_time_oneoption', agenda.content)

        if agenda.function == 'authorize_alternate_time':
            if act.content == 'accept':
                dialog_state['authorize_alternate_time'] = True
                return dialog_act('present_alt_time', ''), dialog_act('present_alt_time', '')
            else:
                dialog_state['authorize_alternate_time'] = False
                return dialog_act('finish_nonauthorized', ''), dialog_act('finish_nonauthorized', '')

        if agenda.function == 'present_alt_time':
            if act.content == 'accept':
                dialog_state['present_alt_time'] = True
                return dialog_act('finish_dialog_alt', ''), dialog_act('finish_dialog_alt', '')
            else:
                dialog_state['present_alt_time'] = False
                return dialog_act('finish_dialog_alt', ''), dialog_act('finish_dialog_alt', '')


    return dialog_act('', ''), dialog_act('', '')

def check_slots_filled(dialog_state):
    if 'alternate_time' in dialog_state:
        prefix = 'alternate_'
    if 'final_time' in dialog_state:
        prefix = 'final_'

    if not dialog_state[prefix+'date']:
        new_act = dialog_act('ask_date', None)
        agenda = dialog_act('ask_date', None)
        return new_act,agenda
            
    elif not dialog_state[prefix+'time']:
        new_act = dialog_act('ask_time', None)
        agenda = dialog_act('ask_time', None)
        return new_act,agenda
    else:
        return dialog_act('finish_dialog_alt', ''), dialog_act('','')