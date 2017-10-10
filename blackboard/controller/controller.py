def update_solution(partial_solution, userID, notification, notification_answer):
	# Recebe três JSON: a representação parcial da solução, a notificação que foi respondida e como ela foi respondida
	# E um int: o userID de quem respondeu à notificação

	if notification['task'] == 'accept_invite':
		if not notification_answer['accept_invite']:
			# retira o participante da lista de participantes e das listas de usuarios pendentes
			partial_solution['event']['participants'][:] = [d for d in partial_solution['event']['participants'] if d.get('id') != userID]
			for time in partial_solution['possible_times']:
				if userID in time['users_pending']:
					time['users_pending'].remove(userID)
		else:
			partial_solution['possible_times'][0]['users_pending'].remove(userID)
			if notification_answer['accept_original_time']:
				partial_solution['possible_times'][0]['users_confirmed'].append(userID)
			else:
				partial_solution['possible_times'][0]['users_declined'].append(userID)	
			if notification_answer['propose_alternate_time']:
				partial_solution['possible_times'].append({'date': notification_answer['alternate_date'],
															'time': notification_answer['alternate_time'],
															'users_pending': get_userIDs(partial_solution, userID),
															'user_confirmed':[userID],
															'users_declined':[]})

		return partial_solution

	if notification['task'] == 'check_alternate_time':
		for possible_time in partial_solution['possible_times']:
			if possible_time['date'] == notification['alternate_time']['date'] and possible_time['time'] == notification['alternate_time']['time']:
				
				possible_time['users_pending'].remove(userID)
				if notification_answer['accept_alternate_time']:
					possible_time['users_confirmed'].append(userID)
				else:
					possible_time['users_declined'].append(userID)
		return partial_solution



	return partial_solution

def get_userIDs(partial_solution, userID):
	# Retorna as user IDs participantes do evento, retirando a user ID
	IDs = []

	IDs.append(partial_solution['event']['host']['id'])
	for participant in partial_solution['event']['participants']:
		if participant['id'] != userID:
			IDs.append(participant['id'])

	return IDs

def generate_notifications(partial_solution, info):
	pass

def eval_solution(partial_solution):
	for possible_time in partial_solution['possible_times']:
		if possible_time['users_pending']:
			return False

	return True