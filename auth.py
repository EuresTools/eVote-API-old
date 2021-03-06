from functools import wraps
from flask import request, jsonify, abort
import models

# Check if the username exists and that the password is valid.
def check_auth(username, password):
    user = models.User.query.filter_by(username=username).first()
    if user == None:
        return False
    return user.verify_password(password)

# Check if the given username belongs to an admin.
def is_admin(username):
    user = models.User.query.filter_by(username=username).first()
    if user == None:
        return False
    return user.is_admin

# Check if the given username belongs to an organizer.
def is_organizer(username):
    user = models.User.query.filter_by(username=username).first()
    if user == None:
        return False
    organizer = models.Organizer.query.filter_by(user=user).first()
    if organizer == None:
        return False
    return True

def authenticate_response():
    abort(401)
    #response = jsonify(status='fail', data=None)
    #response.status_code = 401
    #return response

def forbidden_response():
    abort(403)
    #response = jsonify(status='fail', data=None)
    #response.status_code = 403
    #return response
 
# Make sure the user is authenticated.
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate_response()
        return f(*args, **kwargs)
    return decorated

# Make sure the user is authenticated and an admin.
def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate_response()
        elif not is_admin(auth.username):
            return forbidden_response()
        return f(*args, **kwargs)
    return decorated

# Make sure the user is authenticated and an organizer.
def requires_organizer(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate_response()
        elif not is_organizer(auth.username):
            return forbidden_response()
        return f(*args, **kwargs)
    return decorated

def get_user():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return None
    user = models.User.query.filter_by(username=auth.username).first()
    return user

def get_organizer():
    user = get_user()
    if user == None:
        return None
    organizer = user.organizer
    return organizer
