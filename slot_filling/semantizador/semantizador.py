from dialog_act import *
from Constants import *
import apiai, json
import sys

sys.path.append('./slot_filling/semantizador/')

import semantizador_yorncancel as syorn
import semantizador_final as sf

# Abre sessão do API.AI
ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
session_id = ai.session_id

old_slots = []  # entidades reconhecidas na última consulta ao API.AI

def semantize_msg(msg):

    global old_slots

    new_acts = [] # lista de atos dialogais a ser retornada

    msg = msg.lower()  #lowercase

    # Primeiro caso tratado: fala é um 'sim' ou 'nao'
    syorn_function,syorn_content = syorn.yorncancel(msg)
    
    if syorn_function:
        new_act = dialog_act(syorn_function, syorn_content)
        new_acts.append(new_act)

    # Segundo caso: Localiza nomes de pessoas, entidades relacionamento e locais
    
    #Locais
    #Lista interna
    
    #Pessoas:
    #Oque sobrar de sintagmas nominais do cogroo
    
    # Relacionamento    
    # especificação de participantes por relacionamento, ex: "marque com meu irmão, minha mãe" 
    # Procura por referências a palavras que representem relacionamentos familiares ex: "irmão", "tia", "sobrinho"
    # Achada a referência, se processa os casos que se referem a um familiar de algum conhecido ou seu próprio e agrupa a entidade corretamente

    non_relationship_list,places_list, relationship_list = sf.get_all_entities(msg)
    
    if relationship_list:
        new_act = dialog_act('inform_participants_by_relationship', relationship_list)
        new_acts.append(new_act)

    if non_relationship_list:
        new_act = dialog_act('inform_participants', non_relationship_list)
        new_acts.append(new_act)

    # if places_list:
    #     new_act = dialog_act('inform_place', places_list)
    #     new_acts.append(new_act)

    # Quarto: local
    x = max(msg.rfind('no '), msg.rfind(' na '))     # informa local
    if x > -1:      # achamos alguma das expressões e ela começa no índice x
        new_act = dialog_act('inform_place', msg[x+3:])
        new_acts.append(new_act)


    # Terceiro: entidades reconhecíveis pelo API.AI (datas, horários, tipos de compromisso, verbos que
    # indicam a intenção de marcar um compromisso)
    # Manda /query com o input do usuário para o API.AI
   
    api_acts = get_apiai_acts(msg)
    
    if api_acts:
        new_acts += api_acts               

    if not new_acts:
        new_act = dialog_act(None, msg)
        new_acts.append(new_act)

    return new_acts

def get_apiai_acts(msg):

    global old_slots

    request = ai.text_request()
    request.session_id = session_id
    request.query = msg

    # Pega as entities reconhecidas
    response = json.loads(request.getresponse().read())


    print("\n\nResposta da API.AI:\n")
    print(response)

    if not 'result' in response:
        print('NETWORK ERROR')
        return None

    if not 'parameters' in response['result']: # não houve resposta
        print('NETWORK ERROR')
        return None

    slots = response['result']['parameters']
    
    if 'verbos-compromisso' not in slots:
        return None

    api_acts = compare_dicts(slots, old_slots)
    old_slots = slots

    return api_acts


def compare_dicts(new, old):

    # compara dois dicionários para ver que entidades foram reconhecidas
    # na fala atual. Isso é feito pq o API.AI "lembra" e sempre retorna
    # todas as entidades reconhecidas no diálogo inteiro até o tempo presente.

    slots = ['verbos-compromisso','tipo-compromisso', 'date', 'time']
    entities_recognized = {}

    if not old:
        for slot in slots:
            if new[slot]:
                entities_recognized[slot] = new[slot]

    # elif 'verbos-compromisso' not in new:
    #     return None

    else:
        for slot in slots:
            if new[slot] and not old[slot]:
                entities_recognized[slot] = new[slot]
            elif new[slot] != old[slot]:  
                entities_recognized[slot] = new[slot]

    new_act = generate_act(entities_recognized)
    return new_act

def generate_act(entities_recognized):
    
    # a partir das entidades reconhecidas na fala do uśuário,
    # compõe o ato dialogal correspondente a ser passado ao GD.
    # nesse caso, o ato dialogal contém uma lista de funções e uma
    # lista de conteúdos, cada par representando uma entidade reconhecida
    # a ser guardada pelo GD

    acts = []

    if not entities_recognized:
        return None
    else:
        new_act = dialog_act('inform_intent', True)
        acts.append(new_act)

    for entity in entities_recognized:
        if entity == 'tipo-compromisso':
            new_act = dialog_act('inform_type', '')
        if entity == 'date':
            new_act = dialog_act('inform_date', '')
        if entity == 'time':
            new_act = dialog_act('inform_time', '')
        if entity != 'verbos-compromisso':
            new_act.content = entities_recognized[entity]
        acts.append(new_act)

    return acts