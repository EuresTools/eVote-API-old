#!flask/bin/python
from flask import Flask, jsonify, request, json, abort
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from datetime import datetime

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
        code = 500
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
from parser import *
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
        # If no code is specified, check if an organizer is making the request.
        organizer = auth.get_organizer()
        if not organizer:
            abort(404)
        else:
            # Give the organizer a list of all his polls.
            polls = Poll.query.filter_by(organizer=organizer).all()
            data = {}
            data['polls'] = []
            for poll in polls:
                data['polls'].append(poll.to_dict())
            return jsonify(status='success', data=data)

    # Look up the given vote code and use it to retrieve the poll.
    code = Code.query.filter_by(code=vote_code).first()
    if not code:
        abort(404)
    # Has the code already been used?
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
    organizer = auth.get_organizer()
    if not organizer:
        abort(403)
    json = request.get_json()
    poll, error = parse_poll(json)
    if error:
        return jsonify(status='fail', data=error), 400

    # Attatch the organizer to the poll and save it.
    poll.organizer = organizer
    db.session.add(poll)
    for option in poll.options:
        db.session.add(option)
    db.session.commit()
    return jsonify(status='success', data=poll.to_dict()), 201


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

    elif method == 'PUT':
        json = request.get_json()
        new_poll, error = parse_poll(json)
        if error:
            return jsonify(status='fail', data=error), 400

        # Don't allow editing of a poll that already has votes.
        votes = poll.votes.all()
        if votes:
            return jsonify(status='fail', message='The poll already has some votes and cannot be edited'), 403

        poll.question = new_poll.question
        poll.select_min = new_poll.select_min
        poll.select_max = new_poll.select_max
        poll.start_time = new_poll.start_time
        poll.end_time = new_poll.end_time

        # Delete all the old options.
        for option in poll.options:
            db.session.delete(option)
        # Replace them with the new ones.
        for option in new_poll.options:
            # This needs to be done in a weird way to prevent new_poll from
            # being saved to the db because of relationship cascading.
            poll.options.append(Option(option=option.option))

        db.session.commit()
        data = {}
        data['poll'] = poll.to_dict()
        return jsonify(status='success', data=data)

    elif method == 'DELETE':
        # Delete all the option objects.
        for option in poll.options:
            db.session.delete(option)
        # Delete all the code objects.
        for code in poll.codes:
            db.session.delete(code)
        # Delete all the vote objects.
        for vote in poll.votes:
            db.session.delete(vote)
        # Delete the poll itself.
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
        data = {}
        data['member'] = member.to_dict()
        return jsonify(status='success', data=data), 201


@app.route('/members/<int:memberId>', methods=['GET', 'PUT', 'DELETE'])
@auth.requires_organizer
def memberById(memberId):
    method = request.method
    organizer = auth.get_organizer()
    if not organizer:
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

@app.route('/polls/<int:pollId>/codes', methods=['GET', 'POST'])
@auth.requires_organizer
def create_code(pollId):
    method = request.method
    organizer = auth.get_organizer()
    if not organizer:
        abort(403)
    poll = Poll.query.filter_by(id=pollId, organizer=organizer).first()
    if not poll:
        abort(404)


    if method == 'GET':
        codes = poll.codes.all()
        data = {}
        data['codes'] = []
        for code in codes:
            data['codes'].append(code.to_dict())
        return jsonify(status='success', data=data)

    elif method == 'POST':
        # TODO: Handle parsing errors.
        json = request.get_json()
        member_ids = json['member_ids']
        codes = []
        for member_id in member_ids:
            member = Member.query.filter_by(id=member_id, organizer=organizer).first()
            if not member:
                abort(404)
            code = Code('bla')
            code.poll = poll
            code.member = member
            db.session.add(code)
            codes.append(code)
        db.session.commit()
        # Note: The codes don't have an id in the db until after commit().
        data = {}
        data['codes'] = []
        for code in codes:
            data['codes'].append(code.to_dict())
        return jsonify(status='success', data=data), 201

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

