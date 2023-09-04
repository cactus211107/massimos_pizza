import sqlite3
import random,string

def generateID(length):
    letters = string.ascii_letters+string.digits
    return ''.join(random.choice(letters) for i in range(length))
def generateInviteCode():
    return "i"+generateID(random.randint(8,16))

def generateCodes(n):
    conn = sqlite3.connect('database.db')
    for _ in range(n):
        conn.cursor().execute('INSERT INTO INVITATIONS VALUES (?)',(generateInviteCode(),))
    conn.commit()
    conn.close()