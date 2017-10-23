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

    elif act.function == "check_alternate_time":
        alt_time = act.content['alternate_time']
        orig_time = act.content['original_time']
        if alt_time['date'] == orig_time['date']:
            msg = ("Alguém propôs fazer o " + act.content['event']['type'] + " do dia " + orig_time['date'] 
                    + " das " + orig_time['time'] + " para as " + alt_time['time'] + ". Você poderia comparecer nesse novo horário?")
        else:
            msg = ("Alguém propôs mudar o seu " + act.content['event']['type'] + " do dia " + orig_time['date'] +
                    "para o dia " + alt_time['date'] + " às " + alt_time['time'] + ". Você poderia comparecer nesse novo horário?")
        return msg

    elif act.function == "authorize_alternate_time":
        alt_time = act.content['alternate_time']
        orig_time = act.content['original_time']
        msg = ('Foi proposto um novo horário para o ' + act.content['event']['type'] + ' do dia ' + orig_time['date']
                + ': ' + alt_time['time'] + ' do dia ' + alt_time['date'] + '. Você quer adicionar esse horário à negociação com os outros'
                + ' participantes?')
        return msg

    elif act.function == 'finish_nonauthorized':
        return 'Ok, esse horário não será inserido na negociação.'

    elif act.function == 'present_alt_time':
        return 'E você pode comparecer nesse novo horário?'



    elif act.function == 'schedule_event':
        event = act.content
        msg = ("O " + event['type'] + " organizado por " + event['host'] + " acontecerá no dia " + event['date'] + " às " + event['time']
                + " no local " + event['local'] + ". " + ", ".join(event['participants']) + " confirmaram presença. Vocẽ gostaria de " +
                "incluir esse evento no seu Google Calendar?")
        return msg

    elif act.function == 'schedule_success':
        return "Evento inserido!"
    elif act.function == 'schedule_not_needed':
        return "OK! Aproveite seu compromisso."

    elif act.function == 'decide_final_time_oneoption':
        time = act.content['possible_times'][0]
        msg = ('Há uma opção de horário com o maior número de participantes: ' + time['date'] + " às " + time['time'] + ". " + 
                ", ".join(time['participants']) + " confirmaram presença. Você gostaria de marcar o evento nesse horário?")
        return msg

    elif act.function == 'decide_final_time_multoptions':
        times = act.content['possible_times']
        msg = 'Há algumas opções de horário com o mesmo número máximo de participantes: \n'
        for time in times:
            msg += "\nÀs " + time['time'] + " do dia " + time['date'] + ', ' +", ".join(time['participants']) + " podem estar presentes.\n"
        msg += "Você pode falar o horário escolhido ou cancelar o evento."
        return msg

    elif act.function == 'cancel_event':
        return 'Você gostaria de cancelar o evento?'

    if not act.function:
        return("Não entendi. Vocẽ quer marcar um compromisso?")
    
    if act.function == 'handle_error':
        return("Não entendi, tente dizer mais sobre o seu compromisso")

    elif act.function == None:
        pass
    else:
        print('funcao nao reconhecida pelo GL:' + str(act.function))




    return("Não entendi. Vocẽ quer marcar um compromisso?")