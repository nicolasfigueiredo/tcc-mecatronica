def update_solution(partial_solution, userID, notification, notification_answer):
	# Recebe dois JSON: o relativo à representação parcial da solução e o relativo à uma resposta de um usuário à uma notificação
	# e o userID de quem respondeu à notificação

	if notification['task'] == 'accept_invite':
		if notification_answer['accept_invite'] == False:
			# retira o participante da lista de participantes e das listas de usuarios pendentes
			partial_solution['event']['participants'][:] = [d for d in partial_solution['event']['participants'] if d.get('id') != userID]
			for time in partial_solution['possible_times']:
				if userID in time['users_pending']:
					time['users_pending'].remove(userID)

	return partial_solution

def generate_notifications(partial_solution, info):
	pass

def eval_solution(partial_solution):
	pass