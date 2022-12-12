import os
import psycopg2
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta, timezone
from todo import todo


CREATE_TABLE_USERS = (
    """CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, email TEXT NOT NULL UNIQUE,
                                        password TEXT NOT NULL, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                                        update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"""
)
CREATE_STATUS_ENUM = ("CREATE TYPE status AS ENUM ('NotStarted', 'OnGoing', 'Completed');")

CREATE_TABLE_TODO = (
    """CREATE TABLE IF NOT EXISTS todo (id SERIAL PRIMARY KEY, name TEXT, description TEXT DEFAULT NULL,
                                        user_id INTEGER, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                                        update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, status status,
                                        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);"""
)

SIGN_IN_USER = ("SELECT id FROM users WHERE email = %s AND password = %s;")

VERIFY_USER = ("SELECT * FROM users WHERE email = %s;")


INSERT_USER_RETURN_EMAIL = ("""INSERT INTO users (email, password) VALUES (%s, %s) RETURNING email;""")

INSERT_TODO_RETURN_NAME = (
    """INSERT INTO todo (name, description, user_id, status) VALUES (%s, %s, %s, %s) RETURNING name;"""

)

CHANGE_PASSWORD = ("UPDATE users SET password = %s WHERE email = %s;")

GET_ALL_TODO = ("SELECT * FROM todo WHERE user_id = %s;")

SELECT_TODO = ("SELECT * FROM todo WHERE user_id = %s and status = %s;")

VERIFY_TODO = ("SELECT * FROM todo WHERE id = %s and user_id = %s;")

UPDATE_TODO = ("UPDATE todo SET name = %s, description = %s, update_date = %s, status = %s WHERE id = %s AND user_id = %s;")

DELETE_TODO = ("DELETE FROM todo where id = %s and user_id = %s;")

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
EXPIRESSECONDS = int(os.getenv("EXPIRESSECONDS"))
JWTSECRET = os.getenv("JWTSECRET") #generated from uuid.uuid4().hex


#create new user
def createUser(email, hashed_password):
    try:
        connection = psycopg2.connect(DATABASE_URL)
        with connection:
            with connection.cursor() as cursor:
                #check if the user already exist
                cursor.execute(VERIFY_USER, (email,))
                rows = cursor.fetchall()
                if cursor.rowcount == 1:
                    return  {"Error" : "Could not create user", "User Id " : f"{email} already exist"}, 400

                #create user if new
                cursor.execute(INSERT_USER_RETURN_EMAIL, (email, hashed_password,))
                id = cursor.fetchone()[0]
                return  {"message" : f"User Id {id} created."}, 201
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        if connection is not None:
            cursor.close()
            connection.close()
        return False

    finally:
        if connection is not None:
            cursor.close()
            connection.close()

#check if the user exist
def verifyUser(email,hashed_password):
    try:
        connection = psycopg2.connect(DATABASE_URL)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(SIGN_IN_USER, (email, hashed_password,))
                #cursor.execute(query)
                rows=cursor.fetchall()
                if cursor.rowcount == 1:
                    for row in rows:
                        token = jwt.encode({
                            'user_id': email,
                            'exp' : datetime.utcnow() + timedelta(seconds = EXPIRESSECONDS)
                        }, JWTSECRET, algorithm='HS256')
                        return token                     
                                           
                else:
                    return False

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        if connection is not None:
            cursor.close()
            connection.close()
        return False

    finally:
        if connection is not None:
            cursor.close()
            connection.close()

#get user id
def getUserId(current_user):
    try:
        connection = psycopg2.connect(DATABASE_URL)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(VERIFY_USER, (current_user,))
                user_id=cursor.fetchone()[0]
                return user_id  

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        if connection is not None:
            cursor.close()
            connection.close()
        return False

    finally:
        if connection is not None:
            cursor.close()
            connection.close()


#change password for logged in user
def changePassword(current_user, new_hashed_password):
    try:
        connection = psycopg2.connect(DATABASE_URL)
        with connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(CHANGE_PASSWORD, (new_hashed_password, current_user,))
                    return {"Success" : "Password changed"}, 201
                         
                except (Exception, psycopg2.DatabaseError) as e1:
                    print(e1)
                    if connection is not None:
                        cursor.close()
                        connection.close()
                    return False

    except (Exception, psycopg2.DatabaseError) as e2:
        print(e2)
        if connection is not None:
            cursor.close()
            connection.close()
        return False

    finally:
        if connection is not None:
            cursor.close()
            connection.close()

#get to do list for logged in user
def selectTodo(user_id, query_status):
    try:
        connection = psycopg2.connect(DATABASE_URL)
        with connection:
            with connection.cursor() as cursor:
                try:
                    if query_status is not None:
                        cursor.execute(SELECT_TODO, (user_id, query_status,))
                    else:
                        cursor.execute(GET_ALL_TODO, (user_id,))
                    rows=cursor.fetchall()
                    if cursor.rowcount >= 1:
                        todos=[]
                        for row in rows:
                            values = todo(row[0], row[1], row[2], row[4], row[5], row[6])
                            todos.append(values.__dict__)
                            
                        return {"Todos" : todos}, 200
                         
                except (Exception, psycopg2.DatabaseError) as e1:
                    print(e1)
                    if connection is not None:
                        cursor.close()
                        connection.close()
                    return False

    except (Exception, psycopg2.DatabaseError) as e2:
        print(e2)
        if connection is not None:
            cursor.close()
            connection.close()
        return False

    finally:
        if connection is not None:
            cursor.close()
            connection.close()


#create new todo for logged in user
def createTodo(user_id, name, description, status):
    try:
        connection = psycopg2.connect(DATABASE_URL)
        with connection:
            with connection.cursor() as cursor:            
                #create new todo
                cursor.execute(INSERT_TODO_RETURN_NAME, (name, description, user_id, status, ))
                todo_name = cursor.fetchone()[0]
                return  {"New Todo created" : todo_name}, 201
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        if connection is not None:
            cursor.close()
            connection.close()
        return False

    finally:
        if connection is not None:
            cursor.close()
            connection.close()

#update a todo
def updateTodo(user_id, name, description, status, todo_id):
    try:
        connection = psycopg2.connect(DATABASE_URL)
        with connection:
            with connection.cursor() as cursor:             
                #update todo
                date = datetime.now(timezone.utc)
                ct = date.strftime('%Y-%m-%d %H:%M:%S')
                try:
                    cursor.execute(UPDATE_TODO, (name, description, ct, status, todo_id, user_id, ))
                    return {"Success" : "Todo Updated"}
                         
                except (Exception, psycopg2.DatabaseError) as e1:
                    print(e1)
                    if connection is not None:
                        cursor.close()
                        connection.close()
                    return False
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        if connection is not None:
            cursor.close()
            connection.close()
        return False

    finally:
        if connection is not None:
            cursor.close()
            connection.close()

#verify a todo
def verifyTodo(user_id, todo_id):
    try:
        connection = psycopg2.connect(DATABASE_URL)
        with connection:
            with connection.cursor() as cursor:
                #verify todo
                cursor.execute(VERIFY_TODO, (todo_id, user_id, ))
                rows = cursor.fetchall()
                if cursor.rowcount >= 1:
                    return True                         
                else:
                    return False
    except:
        if connection is not None:
            cursor.close()
            connection.close()
        return False

    finally:
        if connection is not None:
            cursor.close()
            connection.close()

#delete todo
def deleteTodo(user_id, todo_id):
    try:
        connection = psycopg2.connect(DATABASE_URL)
        with connection:
            with connection.cursor() as cursor:
                #deleting todo
                cursor.execute(DELETE_TODO, (todo_id, user_id,))
                return {'Deleted todo' : todo_id}, 201
    except:
        if connection is not None:
            cursor.close()
            connection.close()
        return False

    finally:
        if connection is not None:
            cursor.close()
            connection.close()