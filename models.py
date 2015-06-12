from app import db
import json
from passlib.apps import custom_app_context as password_context

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, index=True, default=False)

    # Verify a plaintext password against the saved hash.
    # Returns True if the password matches, False otherwise.
    def verify_password(self, password):
        return password_context.verify(password, self.password_hash)

    def __init__(self, username, password, is_admin=False):
        self.username = username
        self.password_hash = password_context.encrypt(password)
        self.is_admin = is_admin

    def __repr__(self):
        return '<User %r>' % (self.username)

    def to_dict(self):
        data = {}
        data['id'] = self.id
        data['username'] = self.username
        data['is_admin'] = self.is_admin
        return data

class Organizer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('organizer', uselist=False), uselist=False)
    members = db.relationship('Member', backref=db.backref('organizer', uselist=False), lazy='dynamic')
    polls = db.relationship('Poll', backref=db.backref('organizer', uselist=False), lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Organizer %r>' % (self.name)

    def to_dict(self):
        data = {}
        data['id'] = self.id
        data['name'] = self.name
        return data

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    group = db.Column(db.String(120), index=True)

    organizer_id = db.Column(db.Integer, db.ForeignKey('organizer.id'))
    contacts = db.relationship('Contact', backref='member')
    codes = db.relationship('Code', backref='member', lazy='dynamic')
    votes = db.relationship('Vote', backref='member', lazy='dynamic')

    def __init__(self, name, group):
        self.name = name
        self.group = group

    def __repr__(self):
        return '<Member %r>' % (self.name)

    def to_dict(self):
        data = {}
        data['id'] = self.id
        data['name'] = self.name
        data['group'] = self.group
        data['contacts'] = []
        for contact in self.contacts:
            data['contacts'].append(contact.to_dict())
        return data

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    email = db.Column(db.String(80), index=True)

    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<Contact %r>' % (self.name)

    def to_dict(self):
        data = {}
        data['id'] = self.id
        data['name'] = self.name
        data['email'] = self.email
        return data

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    question = db.Column(db.Text)
    select_min = db.Column(db.Integer)
    select_max = db.Column(db.Integer)

    organizer_id = db.Column(db.Integer, db.ForeignKey('organizer.id'))
    options = db.relationship('Option', backref='poll')
    codes = db.relationship('Code', backref='poll', lazy='dynamic')
    votes = db.relationship('Vote', backref='poll', lazy='dynamic')

    def __repr__(self):
        return '<Poll %r>' % (self.question)

    def to_dict(self):
        data = {}
        data['id'] = self.id
        data['question'] = self.question
        data['select_min'] = self.select_min
        data['select_max'] = self.select_max
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat()
        data['organizer'] = self.organizer.to_dict()
        data['options'] = []
        for option in self.options:
            data['options'].append(option.to_dict())
        return data

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    option = db.Column(db.String(120))
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'))

    def __init__(self, option):
        self.option = option

    def __repr__(self):
        return '<Option %r>' % (self.option)

    def to_dict(self):
        data = {}
        data['id'] = self.id
        data['option'] = self.option
        return data

class Code(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), index=True, unique=True)

    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    vote = db.relationship('Vote', backref='code', uselist=False)

    def __init__(self, code):
        self.code = code

    def __repr__(self):
        return '<Code %r>' % (self.code)

    def to_dict(self):
        data = {}
        data['id'] = self.id
        data['code'] = self.code
        return data

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    code_id = db.Column(db.Integer, db.ForeignKey('code.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'))
    options = db.relationship('Option', secondary='vote_option', backref=db.backref('votes', lazy='dynamic'))

    def to_dict(self):
        data = {}
        data['id'] = self.id
        data['code'] = self.code.to_dict()
        data['poll_id'] = self.poll_id
        data['member_id'] = self.member_id
        data['options'] = []
        for option in self.options:
            data['options'].append(option.to_dict())
        return data

# A relational table between votes and options.
vote_option = db.Table('vote_option',
    db.Column('vote_id', db.Integer, db.ForeignKey('vote.id')),
    db.Column('option_id', db.Integer, db.ForeignKey('option.id'))
)

