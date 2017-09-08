from dialog_act import *
from Constants import *
import apiai, json

# Abre sessão do API.AI
ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
session_id = ai.session_id

old_slots = []  # entidades reconhecidas na última consulta ao API.AI

def semantize_msg(msg):

    global old_slots

    new_act = dialog_act(None, msg) # ato dialogal a ser passado em último caso, para tratamento do erro de entendimento
    msg = msg.lower()  #lowercase

    # Primeiro caso tratado: fala é um 'sim' ou 'nao'
    
    if 'nao' in msg:        # problema com acento: 'no' é reconhecido como 'não'
        new_act.function = 'accept_or_refuse'
        new_act.content = 'refuse'
        return new_act

    if 'sim' in msg:
        new_act.function = 'accept_or_refuse'
        new_act.content = 'accept'
        return new_act

    # Segundo caso: especificação de participantes por relacionamento, ex: "marque com meu irmão, minha mãe" 
    # Procura pelas preposições "meu" e "minha", e assume que o resto da frase contém um ou mais tipos de
    # relacionamento. No ex: ['irmão', 'mãe']

    x = max(msg.rfind('meu '), msg.rfind('minha '))
    if x > -1:      # achamos alguma das expressões e ela começa no índice x
        new_act.function = 'inform_participants_by_relationship'
        new_act.content = msg[x:].split(' ')[1]     # 
        return new_act


    # Terceiro: quero marcar com [lista pessoas]
    if 'com ' in msg:
        new_act.function = 'inform_participants'
        content = msg[msg.find('com '):].split(' ')[1:]     # pega lista de palavras depois de 'com '
        for word in content:    # remove palavras com menos de 3 letras
            if len(word) < 3:
                content.remove(word)
        new_act.content = content
        return new_act

    # Quarto: local
    x = max(msg.rfind('no '), msg.rfind('na '))     # informa local
    if x > -1:      # achamos alguma das expressões e ela começa no índice x
        new_act.function = 'inform_place'
        new_act.content = msg[x+3:]     # pega resto da msg depois de 'no' ou 'na'
        return new_act


    # Quinto: entidades reconhecíveis pelo API.AI (datas, horários, tipos de compromisso, verbos que
    # indicam a intenção de marcar um compromisso)
    # Manda /query com o input do usuário para o API.AI
    request = ai.text_request()
    request.session_id = session_id
    request.query = msg

    # Pega as entities reconhecidas
    response = json.loads(request.getresponse().read())
    print(response)
    if not 'result' in response:
        print('NETWORK ERROR')
        return None

    if not 'parameters' in response['result']: # não houve resposta
        return new_act
    slots = response['result']['parameters']
    if 'verbos-compromisso' not in slots:
        return new_act

    new_act = compare_dicts(slots, old_slots)  
    old_slots = slots               

    if not new_act.function:
        new_act.content = msg

    return new_act


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

    elif 'verbos-compromisso' not in new:
        return dialog_act(None, None)

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

    act = dialog_act([], [])

    if not entities_recognized:
        return act
    else:
        act.function.append('inform_intent')
        act.content.append(True)

    for entity in entities_recognized:
        if entity == 'tipo-compromisso':
            act.function.append('inform_type')
        if entity == 'date':
            act.function.append('inform_date')
        if entity == 'time':
            act.function.append('inform_time')
        if entity != 'verbos-compromisso':
            act.content.append(entities_recognized[entity])

    return act