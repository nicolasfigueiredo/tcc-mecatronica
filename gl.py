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
    elif func == 'ask_all':
        return('O que você gostaria de mudar?')


    elif func == 'confirm_specifications':
        msg = ('Então você gostaria de marcar um ' + dialog_state['type'] + ' no ' + dialog_state['place']
                + ' no dia ' + dialog_state['date'] + ' às ' + dialog_state['time'] + ' com ' + ', '.join(dialog_state['participants'])
                + ' ?')
        return msg  

    elif func == 'confirm_place':
        msg = 'Achamos o local ' + act.content[0] + 'que fica no endereço ' + act.content[1] + '. Confirma?'
        return msg
    elif func == 'confirm_place_notondb':
        msg = 'Não achamos o local' + act.content + ' na nossa base de dados. Confirma o local mesmo assim?'
        return msg

    elif func == None:
        pass
    else:
        print('funcao nao reconhecida pelo GL:' + str(func))

    return("Não entendi. Vocẽ quer marcar um compromisso?")
