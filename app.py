#!flask/bin/python
from flask import Flask, jsonify, request, json, abort
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from datetime import datetime
import random

#__all__ = ['make_json_app']

# TODO: Change id lookups with first() to one() and handle exceptions.

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

        if code in [401, 403, 405, 415]:
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
    if not json:
        abort(415)
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
        if not json:
            abort(415)
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
    data['votes'] = []
    for vote in votes:
        data['votes'].append(vote.to_dict())
    return jsonify(status='success', data=data)


@app.route('/polls/<int:pollId>/votes', methods=['POST'])
# TODO: Test
def post_votesByPollId(pollId):
    poll = Poll.query.filter_by(id=pollId).first()
    if poll == None:
        abort(404)
    # Make sure the poll is open.
    now = datetime.now().replace(tzinfo=None)
    if now < poll.start_time or now > poll.end_time:
        return jsonify(status='fail', message='This poll is currently not open', data=None), 403

    json = request.get_json()
    if not json:
        abort(415)
    vote, error = parse_vote(json, poll)
    if error:
        return jsonify(status='fail', data=error), 400
    db.session.add(vote)
    db.session.commit()

    data = {}
    data['vote'] = vote.to_dict()
    return jsonify(status='success', data=data), 201



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
# TODO: Test
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
        json = request.get_json()
        if not json:
            abort(415)
        member, error = parse_member(json)
        if error:
            return jsonify(status='fail', data=error), 400
        # Attach organizer and save.
        member.organizer = organizer
        db.session.add(member)
        db.session.commit()
        data = {}
        data['member'] = member.to_dict()
        return jsonify(status='success', data=data), 201


@app.route('/members/<int:memberId>', methods=['GET', 'PUT', 'DELETE'])
@auth.requires_organizer
# TODO: Test
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
        json = request.get_json()
        if not json:
            abort(415)
        new_member, error = parse_member(json)
        if error:
            return jsonify(status='fail', data=error)

        # Delete the old contact objects.
        for contact in member.contacts:
            db.session.delete(contact)

        member.name = new_member.name
        member.group = new_member.group
        for new_contact in new_member.contacts:
            contact = Contact(name=new_contact.name, email=new_contact.email)
            member.contacts.append(contact)
        db.session.add(member)
        db.session.commit()

        data = {}
        data['member'] = member.to_dict()
        return jsonify(status='success', data=data)


    elif method == 'DELETE':
        for contact in member.contacts:
            db.session.delete(contact)
        db.session.delete(member)
        db.session.commit()
        return jsonify(status='success', data=None)

@app.route('/polls/<int:pollId>/codes', methods=['GET', 'POST'])
@auth.requires_organizer
def code(pollId):
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
        json = request.get_json()
        if not json:
            abort(415)
        codes, error = parse_codes(json, poll)
        if error:
            return jsonify(status='fail', data=error), 400
        
        for code in codes:
            length = 10
            # Make sure the generated code is unique.
            token = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(length))
            while models.Code.query.filter_by(code=token).first():
                token = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(length))
            code.code = token
            db.session.add(code)
        db.session.commit()

        data ={}
        data['codes'] = []
        for code in codes:
            data['codes'].append(code.to_dict())
        return jsonify(status='success', data=data), 201


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

