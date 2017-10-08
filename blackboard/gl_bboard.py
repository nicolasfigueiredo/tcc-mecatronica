from Constants import *

def generate_response(act):

    # É o gerenciador de linguagem. Retorna a resposta a ser encaminhada ao usuário
    # dependendo do ato dialogal encaminhado pelo GD

    msg = ''

    if act.function == 'propose_invite':
        event = act.content
        msg = ("Você foi convidado por " + event['host'] + " para um " + event['type'] + " com " + ", ".join(event['participants']) +
              " às " + event['time'] + " do dia " + event['date'] + ". Voce aceita esse convite? (aceite se quiser propor outro horário)")
        return msg

    elif act.function == 'decline_invite':
        msg = "OK, você será retirado do evento."
        return msg

    elif act.function == 'accept_original_time':
        msg = "Vocẽ pode comparecer no horário proposto pelo anfitrião?"
        return msg

    elif act.function == 'propose_alternate_time':
        msg = "Você gostaria de propor um horário alternativo para o evento?"
        return msg

    elif act.function == 'ask_alternate_time':
        msg = "Qual?"
        return msg

    elif act.function == 'ask_date':
        return(msg+'Que dia você gostaria de marcar?')
    elif act.function == 'ask_time':
        return(msg+'Que horas você gostaria de marcar?')

    elif act.function == "finish_dialog_alt":
        return "OK! Vou propor esse horário aos outros participantes."

    elif act.function == "finish_dialog":
        return "OK! Vou informar os outros participantes."


    if not act.function:
        return("Não entendi. Vocẽ quer marcar um compromisso?")
    
    if act.function == 'handle_error':
        return("Não entendi, tente dizer mais sobre o seu compromisso")

    elif act.function == None:
        pass
    else:
        print('funcao nao reconhecida pelo GL:' + str(func))




    return("Não entendi. Vocẽ quer marcar um compromisso?")