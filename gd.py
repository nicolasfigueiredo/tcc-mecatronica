from dialog_act import *
from Constants import *
from Agents import *

dialog_state = {'intent': False, 'type': '', 'participants': [], 'place': '', 'date': '', 'time': '', 'finished': False}
agenda_act = dialog_act(None, None) # ato dialogal que esperamos receber no momento

def get_dialog_state():
    return dialog_state


def process_dialog_act(act):

    # Função principal.
    # A implementar: a estrutura geral descrita no TCC do Edson e Lucas
    global agenda_act, dialog_state

    print("\n\nAgenda:\n")
    agenda_act.print()

    if not act.function:
        new_act, agenda = process_error(act, agenda_act, dialog_state)


    # Processa a msg assumindo que seu conteúdo está certo (após a checagem semântica, a ser implementada) 
    else:
        new_act, agenda = process_content(act, agenda_act, dialog_state)
    
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

    if agenda.function == 'inform_type':
        new_act = dialog_act('ask_type', 'retry')
        agenda = dialog_act('inform_type', None)
        return new_act, agenda

    elif agenda.function == 'inform_place':
        new_act = dialog_act('confirm_place_error', act.content)
        agenda = dialog_act('confirm_place', act.content)
        return new_act, agenda

    elif agenda.function == 'inform_participants':
        participants = act.content.split(' ')
        for word in participants:
            if len(word) < 3:
                participants.remove(word)

        new_act = dialog_act('confirm_participants', participants)
        agenda = dialog_act('confirm_participants', participants)
        return new_act, agenda

    elif agenda.function == 'resolve_ambiguity':
        new_act, agenda = Agent_Participants.resolve_ambiguity(act, agenda, dialog_state)
        return new_act, agenda


    elif agenda.function == 'inform_date':
        new_act = dialog_act('ask_date', 'retry')
        agenda = dialog_act('inform_date', None)
        return new_act, agenda        

    elif agenda.function == 'inform_time':
        new_act = dialog_act('ask_time', 'retry')
        agenda = dialog_act('inform_time', None)
        return new_act, agenda

    elif not agenda.function:
        pass

    elif agenda.function[:7] == 'confirm':
        new_act = dialog_act(agenda.function, agenda.content)
        return new_act, agenda

    
    new_act = dialog_act('handle_error', None)
    agenda = dialog_act(None, None)
    return new_act, agenda

def process_content(act, agenda, dialog_state):
    
    # Checa a função do ato dialogal e processa o conteúdo da maneira correspondente
    # Podemos implementar seguindo o modelo dos agentes: nesse caso, cada agente é
    # uma função que processa determinado tipo de msg

    if type(act.function) == list:
        new_act, agenda = Agent_Entities.process_msg(act, dialog_state)
        return new_act, agenda

    if act.function == 'inform_place':    
        new_act, agenda = Agent_Place.process_msg(act, agenda, dialog_state)
        return new_act, agenda
    
    if act.function == 'inform_participants':
        new_act, agenda = Agent_Participants.process_msg(act, dialog_state)
        return new_act, agenda

    if act.function == 'accept_or_refuse':  # checa agenda para ver qual pergunta foi feita
        if agenda.function == 'confirm_place' or agenda.function == 'confirm_place_notondb':
            new_act, agenda = Agent_Place.process_confirm(act, agenda, dialog_state)
            return new_act, agenda

        elif agenda.function == 'confirm_all':
            new_act, agenda = process_confirm_all(act, agenda, dialog_state)
            return new_act, agenda

        elif agenda.function == 'confirm_participants' or agenda.function == 'confirm_full_name' or agenda.function == 'confirm_participants_notondb':
            new_act, agenda = Agent_Participants.process_confirm(act, agenda, dialog_state)
            return new_act, agenda


        else:
            # Tratar o erro
            pass

    return dialog_act('', ''), dialog_act('', '')

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