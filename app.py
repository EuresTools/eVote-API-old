#!flask/bin/python
from flask import Flask, jsonify, request, json, abort
from flask.ext.sqlalchemy import SQLAlchemy
import dateutil.parser
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

#__all__ = ['make_json_app']

def make_json_app(import_name):
    """
    Creates a JSON-oriented Flask app.

    All error responses that you don't specifically
    manage yourself will have application/json content
    type, and will contain JSON like this (just an example):

    { "message": "405: Method Not Allowed" }
    """
    def make_json_error(ex):
        message = str(ex)
        status = ''
        code = 0
        if isinstance(ex, HTTPException):
            code = ex.code
        else:
            code = 500

        if code in [401, 403, 405]:
            status = 'fail'
        else:
            status = 'error'
        response = jsonify(status=status, message=message)
        response.status_code = code
        return response

    app = Flask(import_name)

    for code in default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = make_json_error
    return app

#app = Flask(__name__)
app = make_json_app(__name__)
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
def get_poll():
    vote_code = request.args.get('code')
    if not vote_code:
        abort(404)
    code = Code.query.filter_by(code=vote_code).first()
    if not code:
        abort(404)
    if code.vote != None:
        data = {}
        data['code'] = 'This voting code has already been used'
        return jsonify(status='fail', data=data), 403
    poll = code.poll
    if not poll:
        abort(404)
    data = {}
    data['poll'] = poll.to_dict()
    return jsonify(status='success', data=data), 200

@app.route('/polls', methods=['POST'])
@auth.requires_organizer
def create_poll():
    # TODO: Handle parsing errors!
    try:
        user = auth.get_user()
        organizer = user.organizer
        json = request.get_json()
        poll = Poll()
        poll.organizer = organizer
        poll.question = json['question']
        poll.select_min = json['select_min']
        poll.select_max = json['select_max']
        poll.start_time = dateutil.parser.parse(json['start_time'])
        poll.end_time = dateutil.parser.parse(json['end_time'])
        db.session.add(poll)
        options = json['options']
        for o in options:
            option = Option(o)
            option.poll = poll
            db.session.add(option)
        db.session.commit()
        data = {}
        data['poll'] = poll.to_dict()
        return jsonify(status='success', data=data), 201
    except HTTPException, e:
        print str(e)
        db.session.rollback()
        print 'HTTPException!!!'
        return jsonify(status='error', data=None), e.code
    except Exception, e:
        print str(e)
        db.session.rollback()
        print 'Exception!!!'
        return jsonify(status='error', data=None)


@app.route('/polls/<int:pollId>', methods=['GET', 'PUT', 'DELETE'])
@auth.requires_organizer
def pollById(pollId):
    method = request.method
    organizer = auth.get_organizer()
    if organizer == None:
        abort(403)
    poll = Poll.query.filter_by(organizer=organizer, id=pollId).first()
    if poll == None:
        abort(404)

    if method == 'GET':
        data = {}
        data['poll'] = poll.to_dict()
        return jsonify(status='success', data=data)

    # TODO: Implement PUT.
    elif method == 'PUT':
        return 'PUT /polls/' + str(pollId)
    elif method == 'DELETE':
        db.session.delete(poll)
        db.session.commit()
        return jsonify(status='success', data=None)


# This endpoint is split into two functions because GET requests require
# authentication but not POST requests.
@app.route('/polls/<int:pollId>/votes', methods=['GET'])
@auth.requires_organizer
def get_votesByPollId(pollId):
    organizer = auth.get_organizer()
    if organizer == None:
        abort(403)
    poll = Poll.query.filter_by(organizer=organizer, id=pollId).first()
    if poll == None:
        abort(404)
    # TODO: Paginate.
    votes = poll.votes.all()
    data = {}
    data['votes'] = votes
    return jsonify(status='success', data=data)


@app.route('/polls/<int:pollId>/votes', methods=['POST'])
def post_votesByPollId(pollId):
    poll = Poll.query.filter_by(id=pollId).first()
    if poll == None:
        abort(404)
    # TODO: Handle parsing errors.
    json = request.get_json()
    vote_code = json['code']
    options = json['options']
    # TODO: Finish.

    if not vote_code:
        abort(401)
    code = Code.query.filter_by(code=vote_code, poll=poll).first()
    if not code:
        abort(403)
    if code.vote != None:
        data = {}
        data['code'] = 'This voting code has already been used'
        return jsonify(status='fail', data=data), 403
    return 'POST /polls/' + str(pollId) + '/votes'


@app.route('/polls/<int:pollId>/votes/<int:voteId>', methods=['GET', 'DELETE'])
@auth.requires_organizer
def voteById(pollId, voteId):
    method = request.method
    organizer = auth.get_organizer()
    if organizer == None:
        abort(403)
    poll = Poll.query.filter_by(organizer=organizer, id=pollId).first()
    if poll == None:
        abort(404)
    vote = Vote.query.filter_by(poll=poll, id=voteId)
    if vote == None:
        abort(404)

    if method == 'GET':
        data = {}
        data['vote'] = vote.to_dict()
        return jsonify(status='success', data=data)

    elif method == 'DELETE':
        db.session.delete(vote)
        db.session.commit()
        return jsonify(status='success', data=None)

@app.route('/members', methods=['GET', 'POST'])
@auth.requires_organizer
def members():
    method = request.method
    organizer = auth.get_organizer()
    if organizer == None:
        abort(403)
    if method == 'GET':
        # TODO: Paginate.
        members = Member.query.filter_by(organizer=organizer).all()
        data = {}
        data['members'] = []
        for member in members:
            data['members'].append(member.to_dict())
        return jsonify(status='success', data=data)

    elif method == 'POST':
        # TODO: Handle parsing errors.
        json = request.get_json()
        name = json['name']
        group = json['group']
        contacts = json['contacts']
        member = Member(name, group)
        member.organizer = organizer
        db.session.add(member)
        for c in contacts:
            name = c['name']
            email = c['email']
            contact = Contact(name, email)
            contact.member = member
            db.session.add(contact)
        db.session.commit()


@app.route('/members/<int:memberId>', methods=['GET', 'PUT', 'DELETE'])
@auth.requires_organizer
def memberById(memberId):
    method = request.method
    organizer = auth.get_organizer()
    if organizer == None:
        abort(403)
    member = Member.query.filter_by(id=memberId, organizer=organizer).first()
    if not member:
        abort(404)

    if method == 'GET':
        data = {}
        data['member'] = member.to_dict()
        return jsonify(status='success', data=data)

    elif method == 'PUT':
        # TODO: Implement PUT.
        return 'PUT /members/' + str(memberId)

    elif method == 'DELETE':
        db.session.delete(member)
        db.session.commit()
        return jsonify(status='success', data=None)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

