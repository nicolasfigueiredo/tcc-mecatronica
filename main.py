import sys
sys.path.append("./slot_filling")

import json
import pandas as pd
from rdflib import Graph
from rdflib import URIRef
import slot_filling.main

def check_credentials(user, passwd):
    users = {'userA':'', 'userB':'', 'userC':''}
    if user not in users:
        return False
    if users[user] == passwd:
        return True
    return False

def initialize_main_db():
    # ontologia será user_id.owl, nao precisa guardar na db
    users_dict = {'user_id': [1, 2, 3], 'name':['joao silva', 'maria prado', 'joao neves'],
                 'username': ['userA', 'userB', 'userC'], 'name_on_onthology': ['joaosilva','mariaprado','joaoneves']}
    users_db = pd.DataFrame(users_dict)
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
    event = {'host': host, "participants": participants_invited, 'type': dialog_state['type'], 'local': dialog_state['place'], 'time': dialog_state['time']}
    possible_dates = [{'date': dialog_state['date'], 'users_pending': ids, 'users_confirmed': [host_id], 'users_declined': []}]
    final_dict = {'event': event, 'possible_dates': possible_dates}
    return final_dict


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

    ans = input("Quer marcar um compromisso? (s/n) ")
    if ans == 's':
      print('\nOK!\n')
      event = slot_filling.main.main(onthology_path, onthology_user_ref)

    user_id = int(user_record['user_id'])
    event_json = dialog_state_to_JSON(event, user_id, users_db)
    print(event_json)
    with open('example.json', 'w', encoding='utf8') as outfile:
        json.dump(event_json, outfile, indent=4, ensure_ascii=False)
        
if __name__ == '__main__':
    main()