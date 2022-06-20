import pymysql


def connection():
    return pymysql.connect(
        host="localhost",
        user="fpanel",
        password="@Fpanel123",
        db="flask_panel",
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


def execute(query, type_=2, val=None):
    db = connection()
    cursor = db.cursor()
    if type_ == 1:
        cursor.execute(query)
        return cursor.fetchone()
    elif type_ == 2:
        cursor.execute(query)
        return cursor.fetchall()
    elif type_ == 3:
        cursor.execute(query, val)
        db.commit()
        return True
    elif type_ == 4:
        for i in query:
            cursor.execute(i)
        db.commit()
        return True
    elif type_ == 5:
        cursor.execute(query)
        db.commit()
        return True


def fetchone(query):
    this = execute(query, 1)
    return this


def fetchall(query):
    this = execute(query, 2)
    return this


def insert(query, val):
    execute(query=query, type_=3, val=val)
    return None


def update(query=[]):
    execute(query=query, type_=4)
    return None


def delete(query):
    execute(query=query, type_=5)
    return None
