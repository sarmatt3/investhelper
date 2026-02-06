import sqlite3
import ttech


def dbConnect(sql: str, val: tuple = ()):
    try:
        conn = sqlite3.connect("investhelper.db")
        cursor = conn.cursor()
        cursor.execute(sql, val)
        if sql.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()
        else:
            conn.commit()
            result = True
        conn.close()
        return result
    
    except Exception as e:
        print(f"Ошибка БД: {e}")
        return e



admins = {item[0]:{
    "name": item[1],
    "username": item[2],
    "status": item[3]
    } 
    for item in dbConnect("SELECT * FROM admins")
}    



def adminCheck(uid):
    return uid in admins



def saveUser(uid, name, username):
    try:
        check = dbConnect("SELECT * FROM users WHERE uid = ?", (uid,))
        if not(check == []): 
            return 0
        
        result = dbConnect("INSERT INTO users(uid, name, username) VALUES(?,?,?)", (uid, name, f'@{username}'))
        return result
    
    except Exception as e:
        return e
    

    

