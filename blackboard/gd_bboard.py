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

def get_dialog_state():
    return dialog_state

def process_dialog_act(act):

    # Função principal.
    global agenda_act, dialog_state, event

    print("\n\nAgenda:\n")
    agenda_act.print()

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
 
    new_act = dialog_act('handle_error', None)
    agenda = dialog_act(None, None)
    return new_act, agenda

def process_content(act, agenda, dialog_state, event):
    
    # Checa a função do ato dialogal e processa o conteúdo da maneira correspondente
    # Podemos implementar seguindo o modelo dos agentes: nesse caso, cada agente é
    # uma função que processa determinado tipo de msg

    if type(act.function) == list:

        for function, content in zip(act.function, act.content):
            if function == 'inform_date':
                dialog_state['alternate_date'] = content
            if function == 'inform_time':
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

    return dialog_act('', ''), dialog_act('', '')

def check_slots_filled(dialog_state):
    if not dialog_state['alternate_date']:
        new_act = dialog_act('ask_date', None)
        agenda = dialog_act('ask_date', None)
        return new_act,agenda
        
    elif not dialog_state['alternate_time']:
        new_act = dialog_act('ask_time', None)
        agenda = dialog_act('ask_time', None)
        return new_act,agenda

    else:
        return dialog_act('finish_dialog_alt', ''), dialog_act('','')
