import sys
sys.path.append("../slot_filling")

import semantizador
from dialog_act import *
from Constants import *
import blackboard.gl_bboard
import blackboard.gd_bboard
import json

def process_notification(json_file):

    # Recebe o path para um JSON relativo à uma notificação do usuário.
    # Conduz a conversa até o fim, e depois retorna o dicionário do estado do diálogo,
    # que será utilizado para atualizar a solução de negociação da blackboard

    # # Cria arquivo de log da conversa
    # file_name = 'log' + str(random.randint(0,1000)) + '.txt'

    # Loop principal:
    # 
    # 1 - Recebe o input do usuário pelo terminal
    # 2 - Passa a mensagem ao semantizador, recebendo de volta um ato dialogal
    # 3 - O ato dialogal é passado ao GD, que responde com outro ato dialogal
    # 4 - O ato dialogal é passado ao GL, que responde com uma string a ser comunicada ao usuário
    # with open(file_name, 'w') as f:

    data_file = open(json_file)    
    json_data = json.load(data_file)

    act = blackboard.gd_bboard.startup(json_data)
    msg = blackboard.gl_bboard.generate_response(act)
    print(msg)

    while True:

            print(u"> ", end=u"")
            user_message = input()

            # f.write('u: ' + user_message + '\n')

            print('\n\n\n\n=================================\n')
            dialog_act = semantizador.semantize_msg(user_message)
            print("\n\nAto dialogal retornado pelo semantizador:\n")
            dialog_act.print()

            dialog_act = blackboard.gd_bboard.process_dialog_act(dialog_act)
            print("\n\nAto dialogal retornado pelo GD:\n")
            dialog_act.print()

            print('\n=================================\n\n\n\n')
                        
            msg = blackboard.gl_bboard.generate_response(dialog_act)
            print("< " + str(msg))

            terminator_acts = ['finish_dialog', 'finish_dialog_alt', 'decline_invite', 'finish_nonauthorized', 'schedule_success', 'schedule_not_needed'] # atos que sinalizam o fim do tratamento da notificacao

            if dialog_act.function in terminator_acts:
                break

    data_file.close()
    return json_data, blackboard.gd_bboard.get_dialog_state()


# if __name__ == '__main__':
#     main()