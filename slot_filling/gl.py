from Constants import *

def generate_response(act, dialog_state):

    # É o gerenciador de linguagem. Retorna a resposta a ser encaminhada ao usuário
    # dependendo do ato dialogal encaminhado pelo GD

    func = act.function
    msg = ''

    if not func:
        return("Não entendi. Você quer marcar um compromisso?")
    
    if func == 'handle_error':
        return("Não entendi, tente dizer mais sobre o seu compromisso")

    if act.content == 'retry':
        msg = "Não entendi. "

    if func == 'ask_type':
        return(msg+"Que tipo de compromisso você gostaria de marcar?")
    elif func == 'ask_place':
        return(msg+'Onde você gostaria de marcar o compromisso?')
    elif func == 'ask_date':
        return(msg+'Que dia você gostaria de marcar?')
    elif func == 'ask_time':
        return(msg+'Que horas você gostaria de marcar?')
    elif func == 'ask_participants':
        return(msg+'Com quem você vai?')
    elif func == 'ask_all':
        return('O que você gostaria de mudar?')

    elif func == 'cancel_event':
        return('Agendamento cancelado.')


    elif func == 'confirm_all':
        msg = ('Então você gostaria de marcar um ' + dialog_state['type'] + ' no ' + dialog_state['place']
                + ' no dia ' + prepare_date(dialog_state['date']) + ' às ' + prepare_time(dialog_state['time']) + ' com ' + ', '.join(dialog_state['participants'])
                + '?')
        return msg  

    elif func == 'confirm_place':
        msg = 'Achamos o local ' + act.content[0] + ' que fica no endereço ' + act.content[1] + '. Confirma?'
        return msg

    elif func == 'confirm_place_error':
        msg = 'Não entendi, ' + act.content + ' é o nome do local do compromisso?'
        return msg

    elif func == 'confirm_place_notondb':
        msg = 'Não achamos o local ' + act.content + ' na nossa base de dados. Confirma o local mesmo assim?'
        return msg

    elif func == 'confirm_participants':
        msg = 'Não entendi, você quer convidar ' + act.content + '?'
        return msg

    elif func == 'resolve_ambiguity':
        if len(act.content) > 3:
            prep = act.content[0].split(' ')[0][-1]
            msg = 'Xi, conheço muitas pessoas com esse nome, como '+ prep+' ' + act.content[0] + ' e '+prep+' '  + act.content[1] +'. Qual o nome completo?'
            return msg
        else:
            msg = 'Você está se referindo à ' + ', ou '.join(act.content) +'?'
            return msg

    elif func == 'confirm_full_name':
        msg = 'Você quer convidar ' + act.content + ' para o evento?'
        return msg

    elif func == 'confirm_participants_notondb':
        if type(act.content) is list and len(act.content) > 1:
            msg = 'Não conheço essas pessoas: ' + ', '.join(act.content) +'. Isso quer dizer que não vou conseguir negociar o horário do evento com elas, OK?'
        else:
            msg = 'Não conheço ' + act.content[0] + '. Isso quer dizer que não vou conseguir negociar o horário do evento com essa pessoa, OK?'
        return msg

    elif func == 'retry_relationship':
        msg = 'Desculpe, não conheço ninguém com o tipo de relacionamento ' + act.content + ' com você. Tente especificar a pessoa pelo nome.'
        return msg


    elif func == None:
        pass
    else:
        print('funcao nao reconhecida pelo GL:' + str(func))




    return("Não entendi. Vocẽ quer marcar um compromisso?")


def prepare_date(raw_date):
    return raw_date.split('-')[2] + ' do ' + raw_date.split('-')[1]

def prepare_time(raw_time):
    return raw_time.split(':')[0] + ' horas'