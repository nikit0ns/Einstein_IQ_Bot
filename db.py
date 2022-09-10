from sqlite3 import connect

db = connect("bot.db")
cursor = db.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (uid INT, current_question INTEGER, questions_passed INTEGER, questions_message INTEGER, in_process INTEGER)")
db.commit()


def add(uid: int):
    cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (uid, 0, 0, 0, 0))
    db.commit()


def delete(uid: int):
    cursor.execute("DELETE FROM users WHERE uid=(?)", (uid,))
    db.commit()


def is_exists(uid: int):
    cursor.execute("SELECT * FROM users WHERE uid=(?)", (uid,))
    return bool(cursor.fetchall())


def set_in_process(uid: int, v: bool):
    cursor.execute("UPDATE users SET in_process=(?) WHERE uid=(?)", (1 if v else 0, uid))


def is_in_process(uid: int):
    cursor.execute("SELECT in_process FROM users WHERE uid=(?)", (uid,))
    return bool(int(cursor.fetchone()[0]))


def get_current_questions(uid: int):
    cursor.execute("SELECT current_question FROM users WHERE uid=(?)", (uid,))
    return int(cursor.fetchone()[0])


def change_current_question(uid: int, v: int):
    cursor.execute("UPDATE users SET current_question=(?) WHERE uid=(?)", (v, uid))
    db.commit()


def change_questions_passed(uid: int, v: int):
    cursor.execute("UPDATE users SET questions_passed=(?) WHERE uid=(?)", (v, uid))
    db.commit()


def get_questions_passed(uid: int):
    cursor.execute("SELECT questions_passed FROM users WHERE uid=(?)", (uid, ))
    return int(cursor.fetchone()[0])


def get_questions_message(uid: int):
    cursor.execute("SELECT questions_message FROM users WHERE uid=(?)", (uid, ))
    return int(cursor.fetchone()[0])


def change_questions_message(uid: int, v: int):
    cursor.execute("UPDATE users SET questions_message=(?) WHERE uid=(?)", (v, uid))
    db.commit()
