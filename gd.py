import apiai, json
from processor import *
from Constants import *

def processMsg(msg, state, data):

    #   É o semantizador e gerenciador de diálogo. De acordo com o estado atual do sistema,
    # chama a função correspondente (estão em processor.py) passando 
    # a mensagem do usuário e o vetor de slots to fill. As funções retornam
    # o novo estado do sistema.

    if state == STARTUP:
        newState = processStartup(msg, data)
    if state == TIPO:
        newState = processStartup(msg, data)
    if state == PARTICIPANTES:
        newState = processParticipantes(msg, data)
    if state == LOCAL:
        newState = processLocal(msg, data)
    if state == DATA:
        newState = processData(msg, data)
    if state == HORA:
        newState = processHora(msg, data)
    if state == COMPLETE:
        newState = processFinalize(msg, data)

    return newState


def generateResponse(state, data):

    # É o gerenciador de linguagem. Retorna a resposta a ser encaminhada ao usuário
    # dependendo do estado retornado pelo GD

    if state == STARTUP:
        return("Não entendi. Vocẽ quer marcar um compromisso?")
    if state == TIPO:
        return("Que tipo de compromisso você gostaria de marcar?")
    if state == PARTICIPANTES:
        return("Com quem?")
    
    if state == LOCAL:
        return("Onde?")
    if state == LOCAL_CONFIRM:
        msg = "Ah, o " + data['local'] + " que fica em " + data['endereco'] + "?"
        return(msg)

    if state == DATA:
        return("Que dia?")
    if state == HORA:
        return("Que horas?")
    if state == COMPLETE:
        return("Obrigado, vou tentar marcar o compromisso com os outros!")
        

def main():

    # Começando...

    state = STARTUP
    
    # Slots a serem preenchidos pelo diálogo inicial. 'intent' representa a intenção do usuário de marcar um compromisso
    data = {'intent': False, 'tipo': '', 'participantes': [], 'local': '', 'data': '', 'hora': '', 'endereco': ''}

    while True:

        print(u"> ", end=u"")
        user_message = input()

        if user_message == u"exit":
            break

        # Mensagem do usuário é passado ao processMsg, que atua como semantizador e gerenciador de diálogo e atualiza o 'state'
        state = processMsg(user_message, state, data)
        # Novo estado é passado ao gerenciador de linguagem
        response = generateResponse(state, data)

        print("< %s" % response)

if __name__ == 'main':
    main()