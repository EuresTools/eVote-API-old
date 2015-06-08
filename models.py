from app import db
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

    def __init__(self, username, password, is_admin):
        self.username = username
        self.password_hash = password_context.encrypt(password)
        self.is_admin = is_admin

    def __repr__(self):
        return '<User %r>' % (self.username)

class Organizer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='organizer', uselist=False)
    members = db.relationship('Member', backref='organizer', lazy='dynamic')
    polls = db.relationship('Poll', backref='organizer', lazy='dynamic')


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    group = db.Column(db.String(120), index=True)

    organizer_id = db.Column(db.Integer, db.ForeignKey('organizer.id'))
    contacts = db.relationship('Contact', backref='organization')
    codes = db.relationship('Code', backref='member', lazy='dynamic')
    votes = db.relationship('Vote', backref='member', lazy='dynamic')

    def __init__(self, name, group):
        self.name = name
        self.group = group

    def __repr__(self):
        return '<Member %r>' % (self.name)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    email = db.Column(db.String(80), index=True, unique=True)

    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<Contact %r>' % (self.name)


class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    query = db.Column(db.Text)
    select_min = db.Column(db.Integer)
    select_max = db.Column(db.Integer)

    organizer_id = db.Column(db.Integer, db.ForeignKey('organizer.id'))
    options = db.relationship('Option', backref='poll')
    codes = db.relationship('Code', backref='poll', lazy='dynamic')
    votes = db.relationship('Vote', backref='poll', lazy='dynamic')

    def __repr__(self):
        return '<Poll %r>' % (self.query)

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    option = db.Column(db.String(120))
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'))

    def __repr__(self):
        return '<Option %r>' % (self.option)

class Code(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), index=True, unique=True)

    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    vote = db.relationship('Vote', backref='code', uselist=False)

    def __init__(self, member, poll):
        self.member = member
        self.poll = poll

    def __repr__(self):
        return '<Code %r>' % (self.code)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    code_id = db.Column(db.Integer, db.ForeignKey('code.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'))

