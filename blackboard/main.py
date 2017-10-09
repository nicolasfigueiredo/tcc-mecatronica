import sys
sys.path.append("..")

import semantizador
from dialog_act import *
from Constants import *
import gl_bboard
import gd_bboard

def main():

    # # Cria arquivo de log da conversa
    # file_name = 'log' + str(random.randint(0,1000)) + '.txt'

    # Loop principal:
    # 
    # 1 - Recebe o input do usuário pelo terminal
    # 2 - Passa a mensagem ao semantizador, recebendo de volta um ato dialogal
    # 3 - O ato dialogal é passado ao GD, que responde com outro ato dialogal
    # 4 - O ato dialogal é passado ao GL, que responde com uma string a ser comunicada ao usuário
    # with open(file_name, 'w') as f:

    act = gd_bboard.startup('example_schedule.json')
    msg = gl_bboard.generate_response(act)
    print(msg)

    while True:

            print(u"> ", end=u"")
            user_message = input()

            # f.write('u: ' + user_message + '\n')

            print('\n\n\n\n=================================\n')
            dialog_act = semantizador.semantize_msg(user_message)
            print("\n\nAto dialogal retornado pelo semantizador:\n")
            dialog_act.print()

            dialog_act = gd_bboard.process_dialog_act(dialog_act)
            print("\n\nAto dialogal retornado pelo GD:\n")
            dialog_act.print()

            print('\n=================================\n\n\n\n')
            
            
            msg = gl_bboard.generate_response(dialog_act)
            print("< " + str(msg))
            # f.write('s: ' + msg + '\n')


if __name__ == '__main__':
    main()