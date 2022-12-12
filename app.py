from flask import Flask, request, jsonify
import json
import jwt
import os
import hashlib
import model
from functools import wraps

SECRET_KEY = os.getenv('SECRET_KEY')


# instantiate the Flask app.
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('JWTSECRET')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'X-Access-Token' in request.headers:
            token = request.headers['X-Access-Token']
            
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
  
        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['user_id']
        except:
            return jsonify({'message' : 'Invalid Token'}), 401
        # returns the current logged in users contex to the routes
        return  f(current_user,*args, **kwargs)       
  
    return decorated


#new user creation
#@app.post("/api/v1/signup")
@app.route("/api/v1/signup", methods=["POST"])
def signup():
    email = request.form.get("email")
    password = request.form.get("password")
    hash_object = hashlib.sha1(bytes(password, 'utf-8'))
    hashed_password = hash_object.hexdigest()
    signup = model.createUser(email, hashed_password)
    if signup == False:
        return {'Create user': False}
    else: 
        return json.dumps(signup)
        #return jsonify(signup)
        

    
#user login
#@app.post("/api/v1/signin")
@app.route("/api/v1/signin", methods=["POST"])
def signin():
    email = request.form.get("email")
    password = request.form.get("password")   
    hash_object = hashlib.sha1(bytes(password, 'utf-8'))
    hashed_password = hash_object.hexdigest()
    token = model.verifyUser(email, hashed_password)
  
    if token == False:
        return {'Login failed': 'Unable to verify'}
    else:        
        return jsonify({'token' : token})



#change password for logged in user
#@app.put("/api/v1/changePassword")
@app.route("/api/v1/changePassword", methods=["PUT"])
@token_required
def changePassword(current_user):    
    new_password = request.form.get("new_password")
    confirm_new_password = request.form.get("confirm_new_password")
    if new_password == confirm_new_password:
        #hash new password
        new_hash_object = hashlib.sha1(bytes(new_password, 'utf-8'))
        new_hashed_password = new_hash_object.hexdigest()
        change_password = model.changePassword(current_user, new_hashed_password)
        return {'mesage' : change_password}
    
    else:
        return jsonify({'mesage' : 'Password does not match'}, 400)

#get todo list
@app.route("/api/v1/todos", methods=["GET"])
@token_required
def todos(current_user):
    user_id = model.getUserId(current_user)
    status = request.args.get('status')
    query_status = None
    if status is not None:
        if status not in {'NotStarted', 'OnGoing', 'Completed'}:
            return jsonify({'Select status from' : 'NotStarted or  OnGoing or Completed'}, 400) 
        else:
            query_status = status
    todo = model.selectTodo(user_id, query_status)
    
    if todo == False:
        return jsonify({'Error': 'No todo list'}, 401)
    else:        
        return jsonify({'Showing result' : todo})


#create new todo
@app.route("/api/v1/todos", methods=["POST"])
@token_required
def todos_new(current_user):
    user_id = model.getUserId(current_user)
    name = request.form.get("name")
    description = request.form.get("description")
    status = request.form.get("status")
    new_todo = model.createTodo(user_id, name, description, status)
    if new_todo == False:
        return {'Creating todo': False}
    else: 
        return json.dumps(new_todo)


#update todo
@app.route("/api/v1/todos/<todo_id>", methods = ["PUT"])
@token_required
def update_todo(current_user, todo_id):
    user_id = model.getUserId(current_user)
    todo = model.verifyTodo(user_id, todo_id)
    if todo == False:
        return jsonify({'message': 'No todo found'}, 404)
    name = request.form.get("name")
    description = request.form.get("description")
    status = request.form.get("status")
    update = model.updateTodo(user_id, name, description, status, todo_id)
    if update == False:
        return jsonify({'Error': 'Could not update'}, 401)
    else:        
        return jsonify({'Update' : update}, 200)


#delete todo
@app.route("/api/v1/todos/<todo_id>", methods = ["DELETE"])
@token_required
def delete_todo(current_user, todo_id):
    user_id = model.getUserId(current_user)
    todo = model.verifyTodo(user_id, todo_id)
    if todo == False:
        return jsonify({'message': 'No todo found'}, 404)

    delete = model.deleteTodo(user_id, todo_id)

    if delete == False:
        return jsonify({'Error': 'Could not delete'}, 401)
    else:        
        return jsonify({'Action' : delete})



# run the flask app.
if __name__ == "__main__":
    app.run(debug=True)

