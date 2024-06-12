import sqlite3

db = sqlite3.connect('database.db', check_same_thread=False, isolation_level=None)
db.execute('PRAGMA foreign_keys = ON')

cursor = db.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    name TEXT
)
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tokens (
    token TEXT UNIQUE,
    user_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
)
''')

def create_user(user_id, username, name):
    cursor.execute('''
        INSERT INTO users (user_id, username, name)
        VALUES (?, ?, ?)
    ''', (user_id, username, name))

def get_user(user_id):
    cursor.execute('''
        SELECT * FROM users
        WHERE user_id = ?
    ''', (user_id, ))
    return cursor.fetchone()

def add_token(token, user_id):
    try:
        cursor.execute('''
            INSERT INTO tokens (token, user_id)
            VALUES (?, ?)
        ''', (token, user_id))
        return True
    except sqlite3.IntegrityError:
        return False


def get_token(token):
    cursor.execute('''
        SELECT * FROM tokens
        WHERE token = ?
    ''', (token, ))
    return cursor.fetchone()

def get_all_tokens():
    cursor.execute('''
        SELECT * FROM tokens
    ''')
    response = [
        token[0] for token in cursor.fetchall()
    ]
    return response

def delete_token(token):
    cursor.execute('''
        DELETE FROM tokens
        WHERE token = ?
    ''', (token, ))

def delete_user(user_id):
    try:
        cursor.execute('''
            DELETE FROM users
            WHERE user_id = ?
        ''', (user_id, ))
        return True
    except sqlite3.IntegrityError:
        return False
    
def get_all_users():
    cursor.execute('''
        SELECT * FROM users
    ''')
    return cursor.fetchall()

def get_user_tokens(user_id):
    cursor.execute('''
        SELECT * FROM tokens
        WHERE user_id = ?
    ''', (user_id, ))
    return cursor.fetchall()
