import sys
sys.path.append("./slot_filling")

import json
import pandas as pd
import uuid

from rdflib import Graph
from rdflib import URIRef
import slot_filling.main
import blackboard.process_notification
import blackboard.controller

def check_credentials(user, passwd):
    users = {'userA':'', 'userB':'', 'userC':''}
    if user not in users:
        return False
    if users[user] == passwd:
        return True
    return False

def initialize_main_db():
    # ontologia será user_id.owl, nao precisa guardar na db
    # users_dict = {'user_id': [1, 2, 3], 'name':['joao silva', 'maria prado', 'joao neves'],
    #               'username': ['userA', 'userB', 'userC'], 'name_on_onthology': ['joaosilva','mariaprado','joaoneves']}
    # users_db = pd.DataFrame(users_dict)
    users_db = pd.read_csv('db/users.csv')
    return users_db

def dialog_state_to_JSON(dialog_state, host_id, users_db):
    participants_invited = []
    ids = []
    for participant in dialog_state['participants']:
        id = users_db.query('name == @participant')['user_id']
        if not id.empty:
            participants_invited.append({"id": int(id), "name": participant})
            ids.append(int(id))

    host_name = str(users_db.query('user_id == @host_id')['name'][0])
    host = {"id": host_id, "name": host_name}
    event = {'host': host, "participants": participants_invited, 'type': dialog_state['type'], 'local': dialog_state['place']}
    possible_times = [{'date': dialog_state['date'], 'time': dialog_state['time'],'users_pending': ids, 'users_confirmed': [host_id], 'users_declined': []}]
    final_dict = {'event': event, 'possible_times': possible_times}
    return final_dict

def prepare_invite_json(event_json):
    event = event_json['event']
    event['host'] = event['host']['name']
    event['participants'] = [participant['name'] for participant in event['participants']]
    event['date'] = event_json['possible_times'][0]['date']
    event['time'] = event_json['possible_times'][0]['time']
    invite_json = {'task': 'accept_invite', 'event': event}
    return invite_json

def generate_initial_notifications(event_json, event_id):
    notification_json = prepare_invite_json(event_json)
    notification_id = str(uuid.uuid4())
    notification_path = 'db/notifications/' + notification_id + '.json'
    
    with open(notification_path, 'w', encoding='utf8') as outfile:
            json.dump(notification_json, outfile, indent=4, ensure_ascii=False)

    notification_db = pd.read_csv('db/notifications.csv')
    user_ids = event_json['possible_times'][0]['users_pending']
    new_notifications = []

    for id in user_ids:
        new_notifications.append({'user_id': id, 'event_id': event_id, 'notification_id': notification_id})

    notification_db = notification_db.append(new_notifications)
    notification_db.to_csv('db/notifications.csv')

def check_notifications(user_id):
    notification_db = pd.read_csv('db/notifications.csv')
    user_notifications = notification_db.query('user_id == @user_id')
    if len(user_notifications) == 0:
        return []
    else:
        return user_notifications


def process_notifications(notifications):
    print(notifications)
    for i in range(len(notifications)):
        notification_db_record = notifications.iloc[i]
        id = str(notification_db_record['notification_id'])
        path = 'db/notifications/' + id + '.json'
        notif, ans = blackboard.process_notification.process_notification(path)

        event_id = str(notification_db_record['event_id'])
        partial_solution_path = 'db/events/' + event_id + '.json'
        partial_solution_file = open(partial_solution_path)
        partial_solution_json = json.load(partial_solution_file)

        blackboard.controller.generate_notifications(partial_solution_json, int(notification_db_record['user_id']), event_id, notif, ans)

        new_event = blackboard.controller.update_solution(partial_solution_json, int(notification_db_record['user_id']), notif, ans)
        print(new_event)
        with open(partial_solution_path, 'w', encoding='utf8') as outfile:
            json.dump(new_event, outfile, indent=4, ensure_ascii=False)

        #TODO: eliminar notificação após processada

        


def main():
    user = input('Username:')
    passwd = input('Password:')
    
    if not check_credentials(user, passwd):
      print('Usuário ou senha não encontrados. Saindo...')
      return -1

    users_db = initialize_main_db()
    print(users_db.head())
    user_record = users_db.query('username == @user')
    print(user_record)

    onthology_path = 'onthologies/' + str(int(user_record['user_id'])) + '.owl' 
    onthology_user_ref = str(user_record['name_on_onthology'])

    notifications = check_notifications(int(user_record['user_id']))
    if len(notifications) > 0:
        ans = input('Você possui novas notificações, gostaria de visualizá-las agora? (s/n)')
        if ans == 's':
            process_notifications(notifications)


    ans = input("Você não possui notificações novas. Quer marcar um compromisso? (s/n) ")

    if ans == 's':
      print('\nOK!\n')
      event = slot_filling.main.main(onthology_path, onthology_user_ref)

    if not event['cancelled']:
        event_id = str(uuid.uuid4())
        path = 'db/events/' + event_id + '.json'
        user_id = int(user_record['user_id'])
        event_json = dialog_state_to_JSON(event, user_id, users_db)
        print(event_json)
        with open(path, 'w', encoding='utf8') as outfile:
            json.dump(event_json, outfile, indent=4, ensure_ascii=False)

        generate_initial_notifications(event_json, event_id)


            
if __name__ == '__main__':
    main()