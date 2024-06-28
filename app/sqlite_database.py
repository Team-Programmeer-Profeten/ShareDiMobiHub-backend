import sqlite3
from utils import Pprint
from flask_jwt_extended import create_access_token

import json
import os

class Sqlite_database(Pprint):

    def __init__(self):
        super().__init__(1, "ShareDiMoBiHub", "Database")
        self.conn = sqlite3.connect(f'data/users.db')
        self.cursor = self.conn.cursor()
        
    def initialize_database(self):
        self.create_database()
        dir_path = os.path.dirname(os.path.realpath(__file__))

        with open(os.path.join(dir_path, 'utils', 'users.json')) as users_json:

            self.hardcoded_users = json.load(users_json).get('users')

    

        for user in self.hardcoded_users:
            try:
                self.inject_hardcoded_user(user['username'], user['password'], user['munipicality'])
            except sqlite3.IntegrityError:
                self.printt(f'User {user["username"]} already exists in database, skipping....')
        users_json.close()
    def create_database(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            USERNAME TEXT NOT NULL UNIQUE,
            PASSWORD TEXT NOT NULL,
            MUNICIPALITY TEXT NOT NULL
        )''')
        self.conn.commit()
        self.printt('Connected to database')

    def inject_hardcoded_user(self, username, password, munipicality):
        self.cursor.execute('INSERT INTO users (username, password, municipality) VALUES (?, ?, ?)', (username, password, munipicality))
        self.conn.commit()
    
    def login(self, username, password):
        if (password == 'google'):
            self.cursor.execute('''
                SELECT MUNICIPALITY FROM users WHERE username = ?
            ''', (username,))
        else:
            self.cursor.execute('''
                SELECT MUNICIPALITY FROM users WHERE username = ? AND password = ?
            ''', (username, password))
        user_municipality = self.cursor.fetchone()
        access_token = create_access_token(identity=username)
        if user_municipality:
            return user_municipality, access_token
        return None, None
    
    def get_municipality(self, username):
        self.cursor.execute('''
            SELECT MUNICIPALITY FROM users WHERE username = ?
        ''', (username,))
        return self.cursor.fetchone()