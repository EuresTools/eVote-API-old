#!flask/bin/python
from flask import Flask, jsonify, request
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from models import *
import auth

@app.route('/')
@auth.requires_admin
def index():
    return "Hello, world!"


# The /polls endpoint is split into two functions because POST requests require
# authentication but not GET requests.
@app.route('/polls', methods=['GET'])
def get_polls():
    code = request.args.get('code')
    print code
    return 'GET /polls'

@app.route('/polls', methods=['POST'])
@auth.requires_organizer
def post_polls():
    return 'POST /polls'


@app.route('/polls/<int:pollId>', methods=['GET', 'PUT', 'DELETE'])
@auth.requires_organizer
def pollById(pollId):
    method = request.method
    if method == 'GET':
        return 'GET /polls/' + str(pollId)
    elif method == 'PUT':
        return 'PUT /polls/' + str(pollId)
    elif method == 'DELETE':
        return 'DELETE /polls/' + str(pollId)

# This endpoint is split into two functions because GET requests require
# authentication but not POST requests.
@app.route('/polls/<int:pollId>/votes', methods=['GET'])
@auth.requires_organizer
def get_votesByPollId(pollId):
    return 'GET /polls/' + str(pollId) + '/votes'


@app.route('/polls/<int:pollId>/votes', methods=['POST'])
def post_votesByPollId(pollId):
    return 'POST /polls/' + str(pollId) + '/votes'

@app.route('/polls/<int:pollId>/votes/<int:voteId>', methods=['GET', 'DELETE'])
@auth.requires_organizer
def voteById(pollId, voteId):
    method = request.method
    if method == 'GET':
        return 'GET /polls/' + str(pollId) + '/votes/' + str(voteId)
    elif method == 'DELETE':
        return 'DELETE /polls/' + str(pollId) + '/votes/' + str(voteId)

@app.route('/members', methods=['GET', 'POST'])
@auth.requires_organizer
def members():
    method = request.method
    if method == 'GET':
        return 'GET /members'
    elif method == 'POST':
        return 'POST /members'

@app.route('/members/<int:memberId>', methods=['GET', 'PUT', 'DELETE'])
@auth.requires_organizer
def memberById(memberId):
    method = request.method
    if method == 'GET':
        return 'GET /members/' + str(memberId)
    elif method == 'PUT':
        return 'PUT /members/' + str(memberId)
    elif method == 'DELETE':
        return 'DELETE /members/' + str(memberId)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

