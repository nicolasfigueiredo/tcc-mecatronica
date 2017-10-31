from dialog_act import *
from Constants import *
from Agents import *

dialog_state = {'intent': False, 'type': '', 'participants': [], 'place': '', 'date': '', 'time': '', 'finished': False, 'cancelled': False}
agenda_act = dialog_act(None, None) # ato dialogal que esperamos receber no momento
acts_stack = []

def startup(onthology_path, onthology_user_ref):
    agent_startup(onthology_path, onthology_user_ref)

def get_dialog_state():
    return dialog_state

def get_acts_stack():
    return acts_stack

def pick_highest_priority(acts):
    # Retorna ato de maior prioridade de uma lista, e deleta esse ato da lista
    x = ''

    for i in range(len(acts)):
        if acts[i].function == 'cancel_event':
            x = i
            break
        elif acts[i].function == 'accept_or_refuse':
            x = i
    if not x:
        x = 0

    act = acts[x]
    del(acts[x])
    return act

def process_list_of_acts(acts):
    global acts_stack

    if len(acts) == 1:
        act = acts[0]
    else:
        act = pick_highest_priority(acts)
        acts_stack += acts

    print('stack:')
    print(acts_stack)
    new_act, agenda = process_dialog_act(act)
    return(new_act)

def process_dialog_act(act):
    # Função principal

    global agenda_act, dialog_state

    print('ato a ser processado::')
    act.print()

    print("\n\nAgenda:\n")
    agenda_act.print()

    if not act.function:
        new_act, agenda = process_error(act, agenda_act, dialog_state)


    # Processa a msg assumindo que seu conteúdo está certo (após a checagem semântica, a ser implementada) 
    else:
        new_act, agenda = process_content(act, agenda_act, dialog_state)
        print(acts_stack)
    
    agenda_act = agenda
    print("\n\nEstado do diálogo:\n")
    print(dialog_state)
    print("\n\nAgenda:\n")
    agenda.print()
    
    return new_act, agenda

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
        participants = [word for word in act.content.split(' ') if len(word) >= 3]
        new_act = dialog_act('confirm_participants', participants)
        agenda = dialog_act('confirm_participants', participants)
        return new_act, agenda

    elif agenda.function == 'resolve_ambiguity':
        new_act, agenda = Agent_Participants.resolve_ambiguity(act, agenda, dialog_state)
        if not new_act.function:
            new_act, agenda = take_next_step()
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

def take_next_step():
    if not acts_stack:
        new_act, agenda = check_slots_filled(dialog_state)  # procura quais slots ainda devem ser preenchidos, para fazermos a prox pergunta
        return new_act, agenda
    else:
        return process_dialog_act(pick_highest_priority(acts_stack))

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

def process_content(act, agenda, dialog_state):
    
    # Checa a função do ato dialogal e processa o conteúdo da maneira correspondente
    # Implementado seguindo o modelo dos agentes: nesse caso, cada agente é
    # uma função que processa determinado tipo de msg

    entities_list = ['inform_intent', 'inform_type', 'inform_date', 'inform_time']

    if act.function == 'cancel_event':
        dialog_state['finished'] = True
        dialog_state['cancelled'] = True
        new_act, agenda = dialog_act('cancel_event', '')
        return

    if act.function in entities_list:
        Agent_Entities.process_msg(act, dialog_state)
        new_act, agenda = take_next_step()
        return new_act, agenda

    if act.function == 'inform_place':    
        new_act, agenda = Agent_Place.process_msg(act, agenda, dialog_state)
        if not new_act.function:
            new_act, agenda = take_next_step()
        return new_act, agenda
    
    if act.function == 'inform_participants':
        if agenda.function == 'resolve_ambiguity':
            new_act, agenda = Agent_Participants.resolve_ambiguity(act, agenda, dialog_state)
            if not new_act.function:
                new_act, agenda = take_next_step()
            return new_act, agenda

        new_act, agenda = Agent_Participants.process_msg(act, dialog_state)
        if not new_act.function:
            new_act, agenda = take_next_step()
        return new_act, agenda

    if act.function == 'inform_participants_by_relationship':
        new_act, agenda = Agent_Participants.process_msg_relationship(act, dialog_state)
        if not new_act.function:
            new_act, agenda = take_next_step()
        return new_act, agenda

    if act.function == 'accept_or_refuse':  # checa agenda para ver qual pergunta foi feita
        if agenda.function == 'confirm_place' or agenda.function == 'confirm_place_notondb':
            new_act, agenda = Agent_Place.process_confirm(act, agenda, dialog_state)
            if not new_act.function:
                new_act, agenda = take_next_step()
            return new_act, agenda

        elif agenda.function == 'confirm_all':
            new_act, agenda = process_confirm_all(act, agenda, dialog_state)
            return new_act, agenda

        elif agenda.function == 'confirm_participants' or agenda.function == 'confirm_full_name' or agenda.function == 'confirm_participants_notondb':
            new_act, agenda = Agent_Participants.process_confirm(act, agenda, dialog_state)
            if not new_act.function:
                new_act, agenda = take_next_step()
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