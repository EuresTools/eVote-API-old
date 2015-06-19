from app import *

def generate_poll():
    now = datetime.now()
    # Add a second to be safe.
    now = now + timedelta(seconds=1)
    tomorrow = now + timedelta(days=1)

    poll = {}
    poll['question'] = random_string(20) + '?'
    poll['start_time'] = now.isoformat()
    poll['end_time'] = tomorrow.isoformat()
    poll['select_min'] = 1
    poll['select_max'] = 1
    poll['options'] = ['Yes', 'No', 'Abstain']
    return poll

def generate_member():
    member = {}
    member['name'] = random_string(10)
    member['group'] = random_string(10)
    numcontacts = random.randint(1, 5)
    member['contacts'] = []
    for i in xrange(0, numcontacts):
        contact = {}
        contact['name'] = random_string(10)
        contact['email'] = random_string(7) + '@example.com'
        member['contacts'].append(contact)
    return member


def random_string(length):
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(length))


print 'Dropping tables'
db.drop_all()

print 'Creating tables'
db.create_all()

print 'Adding users and organizer'
admin = User('admin', 'password', True)
db.session.add(admin)

user = User('eurescom', 'password')
db.session.add(user)
organizer = Organizer('Eurescom')
organizer.user = user
db.session.add(organizer)

print 'Creating poll'
polldict = generate_poll()
poll, error = parse_poll(polldict)
poll.organizer = organizer
db.session.add(poll)

print 'Creating member'
memberdict = generate_member()
member, error = parse_member(memberdict)
member.organizer = organizer
db.session.add(member)

print 'Creating voting code'
code = models.Code()
#code.code = 'a'
code.code = random_string(10)
code.member = member
code.poll = poll
db.session.add(code)

print 'Voting code created: %s' % (code.code)

print 'Committing changes'
db.session.commit()

print 'Cleanup done!'



