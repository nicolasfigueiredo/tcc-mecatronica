from Constants import *

def generate_response(act, dialog_state):

    # É o gerenciador de linguagem. Retorna a resposta a ser encaminhada ao usuário
    # dependendo do ato dialogal encaminhado pelo GD

    func = act.function

    if func == '':
        return("Não entendi. Vocẽ quer marcar um compromisso?")
    elif func == 'ask_type':
        return("Que tipo de compromisso você gostaria de marcar?")
    elif func == 'ask_place':
        return('Onde?')
    elif func == 'ask_date':
        return('Que dia?')
    elif func == 'ask_time':
        return('Que horas?')
    elif func == 'ask_participants':
        return('Com quem?')


    elif func == 'confirm_specifications':
        msg = ('Então você gostaria de marcar um ' + dialog_state['type'] + ' no ' + dialog_state['place']
                + ' no dia ' + dialog_state['date'] + ' às ' + dialog_state['time'] + ' com ' + dialog_state['participants']
                + ' ?')
        return msg  

    elif func == 'confirm_address':
        msg = 'Achamos o local ' + dialog_state['place'] + 'que fica no endereço ' + dialog_state['address'] + '. Confirma?'
        return msg
    elif func == 'confirm_place_notondb':
        msg = 'Não achamos o local' + dialog_state['place'] + ' na nossa base de dados. Confirma o local mesmo assim?'
        return msg

    return("Não entendi. Vocẽ quer marcar um compromisso?")
