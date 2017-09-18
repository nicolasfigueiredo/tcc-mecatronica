from semantizador import *
from dialog_act import *
import apiai, json
from Constants import *
from gd import *
from gl import *

def main():

	# Abre sessão do API.AI
	ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
	session_id = ai.session_id

	# Loop principal:
	# 
	# 1 - Recebe o input do usuário pelo terminal
	# 2 - Passa a mensagem ao semantizador, recebendo de volta um ato dialogal
	# 3 - O ato dialogal é passado ao GD, que responde com outro ato dialogal
	# 4 - O ato dialogal é passado ao GL, que responde com uma string a ser comunicada ao usuário

	while True:

	    print(u"> ", end=u"")
	    user_message = input()

	    print('\n\n\n\n=================================\n')
	    dialog_act = semantize_msg(user_message)
	    print("\n\nAto dialogal retornado pelo semantizador:\n")
	    dialog_act.print()

	    dialog_act = process_dialog_act(dialog_act)
	    print("\n\nAto dialogal retornado pelo GD:\n")
	    dialog_act.print()

	    print('\n=================================\n\n\n\n')
	    
	    if get_dialog_state()['finished'] is True:
	    	break
	    
	    msg = generate_response(dialog_act, get_dialog_state())
	    print("< " + str(msg))

	print("\n\n\n\n Diálogo completo.\n\nInicializando blackboard...")

if __name__ == '__main__':
    main()