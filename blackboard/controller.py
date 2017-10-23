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
                # partial_solution['possible_times'].append({ 'authorized': 'False',
                #                                             'date': notification_answer['alternate_date'],
                #                                             'time': notification_answer['alternate_time'],
                #                                             'users_pending': get_userIDs(partial_solution, userID),
                #                                             'user_confirmed':[userID],
                #                                             'users_declined':[]})
                pass
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
        if notification_answer['authorize_alternate_time']:
            if notification_answer['present_alt_time']:
                users_confirmed = [userID, notification['alternate_time']['proposed_by']]
            else:
                users_confirmed = [notification['alternate_time']['proposed_by']]
            partial_solution['possible_times'].append({'date': notification['alternate_time']['date'],
                                                            'time': notification['alternate_time']['time'],
                                                            'users_pending': get_userIDs(partial_solution, users_confirmed),
                                                            'users_confirmed': users_confirmed,
                                                            'users_declined':[]})

    return partial_solution

def get_userIDs(partial_solution, userID):
    # Retorna as user IDs participantes do evento, retirando a user ID
    if type(userID) is not list:
        userID = [userID]

    IDs = []

    if partial_solution['event']['host']['id'] not in userID:
        IDs.append(partial_solution['event']['host']['id'])
    for participant in partial_solution['event']['participants']:
        if participant['id'] not in userID:
            IDs.append(participant['id'])

    return IDs

def generate_notifications(event_json, user_id, event_id, notification, notification_answer):
    new_notifications = []
    # vai criando novas notificações baseadas na resposta a uma notificação, e inserindo os jsons na fila
    # depois, p cada elemento da fila é gerado um id e colocado na DB de notificações


    if notification['task'] == 'accept_invite':
        if notification_answer['accept_invite'] is False:
            # kill other notifications from same event
            notifications_db = pd.read_csv('db/notifications.csv')
            notifications_to_delete = notifications_db.query('user_id == @user_id and event_id == @event_id')
            notifications_to_delete['read'] = True
            notifications_db = pd.concat([notifications_db, notifications_to_delete])
            notifications_db = notifications_db.drop_duplicates(subset=['user_id','notification_id'], keep='last')
            notifications_db.to_csv('db/notifications.csv', columns=['user_id','event_id','notification_id','read'])

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
            new_notification['alternate_time']['proposed_by'] = user_id
            new_notification['alternate_time']['date'] = notification_answer['alternate_date']
            new_notification['alternate_time']['time'] = notification_answer['alternate_time']
            new_notification['event'] = event
            new_notification['task'] = 'authorize_alternate_time'

            new_notifications.append([host_id, event_id, new_notification_id])
            path = 'db/notifications/' + new_notification_id + '.json'
            with open(path, 'w', encoding='utf8') as outfile:
                json.dump(new_notification, outfile, indent=4, ensure_ascii=False)

        elif notification_answer['accept_original_time']:
            if eval_solution(event_json, event_id):
                new_notification = format_final_decision_JSON(event_json)
                new_notification_id = str(uuid.uuid4())
                host_id = event_json['event']['host']['id']
                new_notifications.append([host_id, event_id, new_notification_id])

                path = 'db/notifications/' + new_notification_id + '.json'
                with open(path, 'w', encoding='utf8') as outfile:
                    json.dump(new_notification, outfile, indent=4, ensure_ascii=False)


    if notification['task'] == 'authorize_alternate_time':
        if notification_answer['authorize_alternate_time']:
            # pegar IDs de quem ainda nao respondeu pelo horário: todos menos o host e o proponente do horário
            ids = [notification['alternate_time']['proposed_by']]
            if notification_answer['present_alt_time']:
                ids.append(user_id)

            # criar JSON check_alt_time:
            new_notification = {}
            new_notification_id = str(uuid.uuid4())

            event = copy.deepcopy(event_json['event'])
            event['host'] = event['host']['name']
            event['participants'] = [participant['name'] for participant in event['participants']]
            new_notification['original_time'] = event_json['possible_times'][0]
            new_notification['alternate_time'] = {}
            new_notification['alternate_time']['date'] = notification['alternate_time']['date']
            new_notification['alternate_time']['time'] = notification['alternate_time']['time']
            new_notification['event'] = event
            new_notification['task'] = 'check_alternate_time'
            
            notif_ids = get_userIDs(event_json,ids)
            for id in notif_ids:
                new_notifications.append([id, event_id, new_notification_id])

            path = 'db/notifications/' + new_notification_id + '.json'
            with open(path, 'w', encoding='utf8') as outfile:
                json.dump(new_notification, outfile, indent=4, ensure_ascii=False)

        if notification_answer['present_alt_time']:
            if partial_eval_solution(event_json, event_id):
                new_notification = format_final_decision_JSON(event_json)
                new_notification_id = str(uuid.uuid4())
                host_id = event_json['event']['host']['id']
                new_notifications.append([host_id, event_id, new_notification_id])

                path = 'db/notifications/' + new_notification_id + '.json'
                with open(path, 'w', encoding='utf8') as outfile:
                    json.dump(new_notification, outfile, indent=4, ensure_ascii=False)


    if notification['task'] == 'check_alternate_time':
        if eval_solution(event_json, event_id):
            new_notification = format_final_decision_JSON(event_json)
            new_notification_id = str(uuid.uuid4())
            host_id = event_json['event']['host']['id']
            new_notifications.append([host_id, event_id, new_notification_id])

            path = 'db/notifications/' + new_notification_id + '.json'
            with open(path, 'w', encoding='utf8') as outfile:
                json.dump(new_notification, outfile, indent=4, ensure_ascii=False)

    if notification['task'] == 'decide_final_time':
        new_notification = {}
        new_notification['event'] = {}
        new_notification['task'] = 'schedule_event'
        new_notification['event']['host']  = event_json['event']['host']['name']
        new_notification['event']['type']  = event_json['event']['type']
        new_notification['event']['local'] = event_json['event']['local']
        for possible_time in event_json['possible_times']:
            if possible_time['time'] == notification_answer['final_time'] and possible_time['date'] == notification_answer['final_date']:
                names = get_names_from_ids(possible_time['users_confirmed'])
        new_notification['event']['participants'] = names
        new_notification['event']['date'] = notification_answer['final_date']
        new_notification['event']['time'] = notification_answer['final_time']

        notif_ids = get_ids_from_names(names)
        new_notification_id = str(uuid.uuid4())

        for id in notif_ids:
            new_notifications.append([id, event_id, new_notification_id])

            path = 'db/notifications/' + new_notification_id + '.json'
            with open(path, 'w', encoding='utf8') as outfile:
                json.dump(new_notification, outfile, indent=4, ensure_ascii=False)





    #no fim dessa função, passar lista de tuplas p função que atualiza o csv
    return(insert_notifications(new_notifications))

def format_final_decision_JSON(event_json):

    new_notification = {}
    new_notification['event'] = {}
    threshold = 0
    final_times = []

    for time in event_json['possible_times']:
        if len(time['users_confirmed']) > threshold:
            final_times = []
            final_times.append(time)
            threshold = len(time['users_confirmed'])
        elif len(time['users_confirmed']) == threshold:
            final_times.append(time)

    new_notification['task'] = 'decide_final_time'
    new_notification['event']['host'] = event_json['event']['host']['name']
    new_notification['event']['type'] = event_json['event']['type']
    new_notification['event']['local'] = event_json['event']['local']
    new_notification['possible_times'] = []
    for final_time in final_times:
        entry = {}
        entry['date'] = final_time['date']
        entry['time'] = final_time['time']
        entry['participants'] = get_names_from_ids(final_time['users_confirmed'])
        new_notification['possible_times'].append(entry)
    
    return new_notification


def get_names_from_ids(ids):
    users_db = pd.read_csv('db/users.csv')
    names = []
    for id in ids:
        name = str(users_db.query('user_id == @id').iloc[0]['name']).title()
        names.append(name)
    return names

def get_ids_from_names(names):
    users_db = pd.read_csv('db/users.csv')
    ids = []
    for name in names:
        name = name.lower()
        user_id = int(users_db.query('name == @name').iloc[0]['user_id'])
        ids.append(user_id)
    return ids



def insert_notifications(new_notifications):
    if not new_notifications:
        return

    notification_db = pd.read_csv('db/notifications.csv')
    new_not_db = []

    for notification in new_notifications:
        new_not_db.append({'user_id': notification[0], 'event_id': notification[1], 'notification_id': notification[2], 'read': False})
    
    print(new_notifications)
    print(new_not_db)
    notification_db = notification_db.append(new_not_db, ignore_index=True)
    notification_db.to_csv('db/notifications.csv', columns=['user_id','event_id','notification_id','read'])


def eval_solution(partial_solution, event_id):
    for possible_time in partial_solution['possible_times']:
        if possible_time['users_pending']:
            return False

    host_id = partial_solution['event']['host']['id']
    notifications_db = pd.read_csv('db/notifications.csv')
    if len(notifications_db.query('user_id == @host_id and event_id == @event_id and read == False')) > 0:
        return False

    return True

def partial_eval_solution(partial_solution, event_id):
    for possible_time in partial_solution['possible_times']:
        if possible_time['users_pending']:
            return False
    return True