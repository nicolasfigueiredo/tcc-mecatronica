from dialog_act import *
##from Constants import *
#import apiai, json
import sys

sys.path.append('./slot_filling/semantizador/')

import semantizador_yorncancel as syorn
import semantizador_entities as sf

def semantize_msg(msg):

    new_acts = [] # lista de atos dialogais a ser retornada

    msg = msg.lower()  #lowercase

    # Primeiro caso tratado: fala é um 'sim' ou 'nao'
    syorn_function,syorn_content = syorn.yorncancel(msg)
    
    if syorn_function:
        new_act = dialog_act(syorn_function, syorn_content)
        new_acts.append(new_act)

    # Segundo passo: identificacao de entidades
    non_relationship_list,places_list, relationship_list,types_list,date,time = sf.get_all_entities(msg)
    
    if relationship_list:
        new_act = dialog_act('inform_participants_by_relationship', [x.text for x in relationship_list])
        new_acts.append(new_act)

    if non_relationship_list:
        new_act = dialog_act('inform_participants', [x.text for x in non_relationship_list])
        new_acts.append(new_act)
        
    if places_list:
        new_act = dialog_act('inform_place', [x.text for x in places_list])
        new_acts.append(new_act)
    
    if types_list:
        new_act = dialog_act('inform_type', [x.text for x in types_list])
        new_acts.append(new_act)
        
    if date:
        new_act = dialog_act('inform_date', date)
        new_acts.append(new_act)
        
    if time:
        new_act = dialog_act('inform_time', time)
        new_acts.append(new_act)

    if not new_acts:
        new_act = dialog_act(None, msg)
        new_acts.append(new_act)

    return new_acts