import sqlite3

conn = sqlite3.connect('users.db')

users_dict = {'user_id': [1, 2, 3], 'name':['joao silva', 'maria prado', 'joao neves'],
                 'username': ['userA', 'userB', 'userC'], 'name_on_onthology': ['joaosilva','mariaprado','joaoneves']}
                 