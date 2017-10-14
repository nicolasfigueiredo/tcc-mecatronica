import sys
sys.path.append('./slot_filling')

import semantizador
from dialog_act import *
import apiai, json
from Constants import *
import gd
import gl

def main(onthology_path, onthology_user_ref):

	# # Abre sessão do API.AI
	# ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
	# session_id = ai.session_id

	# # Cria arquivo de log da conversa
	# file_name = 'log' + str(random.randint(0,1000)) + '.txt'

	# Loop principal:
	# 
	# 1 - Recebe o input do usuário pelo terminal
	# 2 - Passa a mensagem ao semantizador, recebendo de volta um ato dialogal
	# 3 - O ato dialogal é passado ao GD, que responde com outro ato dialogal
	# 4 - O ato dialogal é passado ao GL, que responde com uma string a ser comunicada ao usuário
	# with open(file_name, 'w') as f:

		gd.startup(onthology_path, onthology_user_ref)

		while True:

		    print(u"> ", end=u"")
		    user_message = input()

		    # f.write('u: ' + user_message + '\n')

		    print('\n\n\n\n=================================\n')
		    dialog_act = semantizador.semantize_msg(user_message)
		    print("\n\nAto dialogal retornado pelo semantizador:\n")
		    dialog_act.print()

		    dialog_act = gd.process_dialog_act(dialog_act)
		    print("\n\nAto dialogal retornado pelo GD:\n")
		    dialog_act.print()

		    print('\n=================================\n\n\n\n')
		    
		    if gd.get_dialog_state()['finished'] is True:
		    	break
		    
		    msg = gl.generate_response(dialog_act, gd.get_dialog_state())
		    print("< " + str(msg))
		    # f.write('s: ' + msg + '\n')

		print("\n\n\n\n Diálogo completo.\n\nInicializando blackboard...")
		return gd.get_dialog_state()

if __name__ == '__main__':
    main()