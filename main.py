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

	    dialog_act = semantize_msg(user_message)
	    dialog_act.print()

	    dialog_act = process_dialog_act(dialog_act)
	    dialog_act.print()

	    msg = generate_response(dialog_act, get_dialog_state())
	    print("< " + str(msg))

if __name__ == '__main__':
    main()