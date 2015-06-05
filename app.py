#!flask/bin/python
from flask import Flask, jsonify, request
import auth

app = Flask(__name__)

@app.route('/')
@auth.requires_admin
def index():
    return "Hello, world!"

@app.route('/polls', methods=['GET', 'POST'])
def polls():
    method = request.method
    if method == 'GET':
        code = request.args.get('code')
        print code
        return 'GET /polls'
    elif method == 'POST':
        return 'POST /polls'


@app.route('/polls/<int:pollId>', methods=['GET', 'PUT', 'DELETE'])
def pollById(pollId):
    method = request.method
    if method == 'GET':
        return 'GET /polls/' + str(pollId)
    elif method == 'PUT':
        return 'PUT /polls/' + str(pollId)
    elif method == 'DELETE':
        return 'DELETE /polls/' + str(pollId)

@app.route('/polls/<int:pollId>/votes', methods=['GET', 'POST'])
def votesByPollId(pollId):
    method = request.method
    if method == 'GET':
        return 'GET /polls/' + str(pollId) + '/votes'
    if method == 'POST':
        return 'POST /polls/' + str(pollId) + '/votes'

@app.route('/polls/<int:pollId>/votes/<int:voteId>', methods=['GET', 'DELETE'])
def voteById(pollId, voteId):
    method = request.method
    if method == 'GET':
        return 'GET /polls/' + str(pollId) + '/votes/' + str(voteId)
    elif method == 'DELETE':
        return 'DELETE /polls/' + str(pollId) + '/votes/' + str(voteId)

@app.route('/members', methods=['GET', 'POST'])
def members():
    method = request.method
    if method == 'GET':
        return 'GET /members'
    elif method == 'POST':
        return 'POST /members'

@app.route('/members/<int:memberId>', methods=['GET', 'PUT', 'DELETE'])
def memberById(memberId):
    method = request.method
    if method == 'GET':
        return 'GET /members/' + str(memberId)
    elif method == 'PUT':
        return 'PUT /members/' + str(memberId)
    elif method == 'DELETE':
        return 'DELETE /members/' + str(memberId)


if __name__ == '__main__':
    app.run(debug=True)
