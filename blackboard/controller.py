import uuid
import pandas as pd
import json
import copy

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

    if notification['task'] == 'authorize_alternate_time':
        if notification_answer['authorize_alternate_time'] is True:
            partial_solution['possible_times'].append({'date': notification['alternate_time']['date'],
                                                            'time': notification['alternate_time']['time'],
                                                            'users_pending': get_userIDs(partial_solution, userID),
                                                            'user_confirmed':[userID],
                                                            'users_declined':[]})




    return partial_solution

def get_userIDs(partial_solution, userID):
    # Retorna as user IDs participantes do evento, retirando a user ID
    IDs = []

    IDs.append(partial_solution['event']['host']['id'])
    for participant in partial_solution['event']['participants']:
        if participant['id'] != userID:
            IDs.append(participant['id'])

    return IDs

def generate_notifications(event_json, user_id, event_id, notification, notification_answer):
    new_notifications = []
    # vai criando novas notificações baseadas na resposta a uma notificação, e inserindo os jsons na fila
    # depois, p cada elemento da fila é gerado um id e colocado na DB de notificações


    if notification['task'] == 'accept_invite':
        if notification_answer['accept_invite'] is False:
            #TODO: kill other notifications from same event
            pass
        elif notification_answer['propose_alternate_time']:
            
            # Se proposto um novo horário, criar notificação pro HOST para autorizar a negociação desse horário

            new_notification = {}
            new_notification_id = str(uuid.uuid4())
            host_id = event_json['event']['host']['id']
            
            event = copy.deepcopy(event_json['event'])
            event['host'] = event['host']['name']
            event['participants'] = [participant['name'] for participant in event['participants']]
            new_notification['original_time'] = event_json['possible_times'][0]
            new_notification['alternate_time'] = {}
            new_notification['alternate_time']['date'] = notification_answer['alternate_date']
            new_notification['alternate_time']['time'] = notification_answer['alternate_time']
            new_notification['event'] = event
            new_notification['task'] = 'authorize_alternate_time'

            new_notifications.append([host_id, event_id, new_notification_id])
            path = 'db/notifications/' + new_notification_id + '.json'
            with open(path, 'w', encoding='utf8') as outfile:
                json.dump(new_notification, outfile, indent=4, ensure_ascii=False)

            

    #no fim dessa função, passar lista de tuplas p função que atualiza o csv
    return(insert_notifications(new_notifications))

def insert_notifications(new_notifications):
    if not new_notifications:
        return

    notification_db = pd.read_csv('db/notifications.csv')
    new_not_db = []

    for notification in new_notifications:
        new_not_db.append({'user_id': notification[0], 'event_id': notification[1], 'notification_id': notification[2]})
    
    print(new_notifications)
    print(new_not_db)
    notification_db = notification_db.append(new_not_db)
    notification_db.to_csv('db/notifications.csv')


def eval_solution(partial_solution):
    for possible_time in partial_solution['possible_times']:
        if possible_time['users_pending']:
            return False

    return True