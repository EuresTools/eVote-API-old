from app import db
from passlib.apps import custom_app_context as password_context

# Relational table between users and roles.
user_role = db.Table('user_role',
        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), index=True, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Role %r>' % (self.name)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    roles = db.relationship('Role', secondary=user_role, backref=db.backref('users', lazy='dynamic'))
    members = db.relationship('Member', backref='organizer', lazy='dynamic')
    polls = db.relationship('Poll', backref='organizer', lazy='dynamic')

    # Encrypt the password and assign it to the user.
    def hash_password(self, password):
        self.password_hash = password_context.encrypt(password)

    # Verify a plaintext password against the saved hash.
    # Returns True if the password matches, False otherwise.
    def verify_password(self, password):
        return password_context.verify(password, self.password_hash)

    def __init__(self, username, password):
        self.username = username
        self.password_hash = password_context.encrypt(password)

    def __repr__(self):
        return '<User %r>' % (self.username)


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    group = db.Column(db.String(120), index=True)

    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    contacts = db.relationship('Contact', backref='organization')
    codes = db.relationship('Code', backref='member', lazy='dynamic')

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

    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    options = db.relationship('Option', backref='poll')
    codes = db.relationship('Code', backref='poll')

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
