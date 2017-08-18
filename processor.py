import apiai, json
import requests, Levenshtein
from Constants import *
from auxfunc import *

def processStartup(msg, data):
    
    # Processa uma mensagem do usuário quando estamos no primeiro estado do sistema.
    # Nesse estado, assumimos que o usuário tentará marcar um compromisso, talvez já
    # especificando o tipo (ex: "quero marcar um bar", "quero marcar um almoço")
    #
    # O resultado do processamento será o novo estado do sistema, que depende da mensagem do usuário:
    # - Se apenas reconhecermos o intuito do usuário de marcar um compromisso mas não seu tipo
    # (ex: 'quero marcar um compromisso', 'quero sair') o próximo estado será TIPO
    #
    # - Se reconhecermos o intuito e o tipo, o próximo estado será LOCAL
    #
    # - Se não reconhecermos o intuito de marcar um compromisso, permanecemos no estado STARTUP

    nextState = STARTUP

    # Abre sessão do API.AI
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    session_id = ai.session_id

    # Manda /query com o input do usuário para o API.AI
    request = ai.text_request()
    request.session_id = session_id
    request.query = msg

    # Pega as entities reconhecidas
    response = json.loads(request.getresponse().read())
    slots = response['result']['parameters']

    # Checa quais entidades foram reconhecidas, e atualiza o estado do sistema
    if not slots:
        nextState = STARTUP

    if 'verbos-compromisso' not in slots:
        nextState = STARTUP 

    elif not slots['verbos-compromisso']:
        nextState = STARTUP

    elif not slots['tipo-compromisso']:
        data['intent'] = True
        nextState = TIPO

    else:
        data['tipo'] = slots['tipo-compromisso']
        data['intent'] = True
        nextState = PARTICIPANTES

    return nextState

def processParticipantes(msg, data):
    
    # TODO

    return LOCAL

def getNomeLocal(msg):

    # TODO
    # Função utilizada em processLocal()
    # Extrai da fala do usuário (por ex: "quero ir no Quitandinha") o nome do local ("Quitandinha")
    # Ou seja, é o semantizador utilizado quando o sistema está no estado 'aguardando local', nomeado
    # aqui de LOCAL

    # Possível jeito: procurar preposições específicas: 'no', 'na', 'em', etc
    # Talvez retornar False se nao reconhecer nenhuma preposição? ou assumir que a msg só contém o nome do local, sem preposiçao

    return msg

def processLocal(msg, data):

    # Processa uma mensagem do usuário quando estamos esperando o nome do local do compromisso.
    #
    # Primeiramente, processamos a fala completa do usuário para extrair o nome dado (função getNomeLocal)
    # Em seguida, fazemos uma busca no Places API por um local com tal nome. Comparamos o nome
    # do primeiro local obtido com o dado pelo usuário por meio da distância de Leveinshtein, que retorna um índice de 
    # similaridade entre duas strings. 
    # 
    # - Se forem semelhantes, transitamos para LOCAL_CONFIRM
    # - E se forem muito diferentes? TODO
    #
    #

    nomeDado = getNomeLocal(msg)    # Por enquanto, assumimos que getNomeLocal sempre retorna um nome válido de local

    # Formatando a URL para o request á Places API
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    parameters = {'query': nomeDado, 'location': SAOPAULO, 'radius': '5000', 'type': translate_type[data['tipo']], 'key': API_KEY}
    request_url = format_url(base_url, parameters)

    # Recebendo a resposta da API
    r = requests.get(request_url)
    response = r.json()

    # Checar o que veio na resposta, e, se houve algum resultado, checar a similaridade entre o nome do estabelecimento achado e o dado
    if response['status'] == 'OK':
        nomeAchado = response['results'][0]['name']
        enderecoAchado = response['results'][0]['formatted_address']
        
        # Índice de diferença entre duas strings: quanto menor, mais parecidas as duas palavras
        stringDistance = float(Levenshtein.distance(nomeDado, nomeAchado)) / len(nomeDado)

        if stringDistance < 0.2:
            data['local'] = nomeAchado
            data['endereco'] = enderecoAchado 
            nextState = LOCAL_CONFIRM

        # No else, para que estado transitar? Algum que aceita um nome sem ele estar no Places API? Implementar
        else:
            data['local'] = nomeAchado
            data['endereco'] = enderecoAchado 
            nextState = LOCAL_RETRY # ou outro?

    elif response['status'] == 'ZERO_RESULTS':
        nextState = LOCAL_RETRY # ou outro?

    return(nextState)

def processData(msg, data):
    # TODO
    # Mandar fala pro API.AI, ver se ele reconhece data ou hora ou hora e data
    return nextState