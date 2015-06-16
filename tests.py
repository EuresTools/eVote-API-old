import os
import base64
import time
from app import *
import unittest
import tempfile

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

admin = 'admin'
organizer = 'organizer'
password = 'password'

from models import *

class eVoteTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        db.create_all()

        admin = User('admin', 'password', True)
        db.session.add(admin)

        user = User('organizer', 'password')
        db.session.add(user)

        organizer = Organizer('Eurescom')
        organizer.user = user
        db.session.add(organizer)

        db.session.commit()


    def tearDown(self):
        db.drop_all()

    # Get all polls of organizer when none exist.
    def test_get_polls_empty(self):
        res = self.app.get('/polls', headers={'Authorization': 'Basic ' + base64.b64encode(organizer + ":" + password), 'Content-Type': 'application/json'})
        data = res.get_data()
        js = json.loads(data)
        assert not js['data']['polls']


    def test_create_poll(self):
        data = generate_poll()
        # Try without authentication.
        res = self.app.post('/polls', data=json.dumps(data), headers={'Content-Type': 'application/json'})
        assert res.status_code == 401

        # Non-organizer authentication.
        res = self.app.post('/polls', data=json.dumps(data), headers={'Authorization': 'Basic ' + base64.b64encode(admin + ":" + password), 'Content-Type': 'application/json'})
        assert res.status_code == 403

        # With authentication.
        res = self.app.post('/polls', data=json.dumps(data), headers={'Authorization': 'Basic ' + base64.b64encode(organizer + ":" + password), 'Content-Type': 'application/json'})
        assert res.status_code == 201

        res_data = res.get_data()
        js = json.loads(res_data)
        assert js['status'] == 'success'
        poll = js['data']['poll']

        # Compare the data.
        for key in data:
            if key == 'options':
                assert len(data['options']) == len(poll['options'])
                for option in poll['options']:
                    assert option['option'] in data['options']
            else:
                assert poll[key] == data[key]

    def test_create_member(self):
        data = generate_member()

        # Try without authentication.
        res = self.app.post('/members', data=json.dumps(data), headers={'Content-Type': 'application/json'})
        assert res.status_code == 401

        # Non-organizer authentication.
        res = self.app.post('/members', data=json.dumps(data), headers={'Authorization': 'Basic ' + base64.b64encode(admin + ":" + password), 'Content-Type': 'application/json'})
        assert res.status_code == 403

        # With authentication.
        res = self.app.post('/members', data=json.dumps(data), headers={'Authorization': 'Basic ' + base64.b64encode(organizer + ":" + password), 'Content-Type': 'application/json'})
        assert res.status_code == 201

        res_data = res.get_data()
        js = json.loads(res_data)
        member = js['data']['member']
        assert js['status'] == 'success'

        # Compare the data.
        for key in data:
            if key == 'contacts':
                assert len(data['contacts']) == len(member['contacts'])
                for contact in member['contacts']:
                    assert {'name': contact['name'], 'email': contact['email']} in data['contacts']
            else:
                assert member[key] == data[key]

    def test_code_and_vote(self):
        poll = generate_poll()
        res = self.app.post('/polls', data=json.dumps(poll), headers={'Authorization': 'Basic ' + base64.b64encode(organizer + ":" + password), 'Content-Type': 'application/json'})
        assert res.status_code == 201

        res_data = res.get_data()
        js = json.loads(res_data)
        poll_id = js['data']['poll']['id']

        member = generate_member()
        res = self.app.post('/members', data=json.dumps(member), headers={'Authorization': 'Basic ' + base64.b64encode(organizer + ":" + password), 'Content-Type': 'application/json'})
        assert res.status_code == 201

        res_data = res.get_data()
        js = json.loads(res_data)
        member_id = js['data']['member']['id']

        data = {}
        data['member_ids'] = [member_id]

        # Try without authentication
        res = self.app.post('/polls/%d/codes' % (poll_id), data=json.dumps(data), headers={'Content-Type': 'application/json'})
        assert res.status_code == 401

        # Non-organizer authentication.
        res = self.app.post('/polls/%d/codes' % (poll_id), data=json.dumps(data), headers={'Authorization': 'Basic ' + base64.b64encode(admin + ":" + password), 'Content-Type': 'application/json'})
        assert res.status_code == 403

        # With proper authentication.
        res = self.app.post('/polls/%d/codes' % (poll_id), data=json.dumps(data), headers={'Authorization': 'Basic ' + base64.b64encode(organizer + ":" + password), 'Content-Type': 'application/json'})
        assert res.status_code == 201

        res_data = res.get_data()
        js = json.loads(res_data)
        code = str(js['data']['codes'][0]['code'])

        # GET the poll via the code.
        res = self.app.get('/polls?code=%s' % (code))
        assert res.status_code == 200

        res_data = res.get_data()
        js = json.loads(res_data)
        retr_poll_id = js['data']['poll']['id']
        assert retr_poll_id == poll_id

        option_id = js['data']['poll']['options'][0]['id']
        vote = {}
        vote['code'] = code
        vote['options'] = [option_id]

        # Wait for the poll to open to be able to cast the vote.
        time.sleep(1)
        res = self.app.post('/polls/%d/votes' % (poll_id), data=json.dumps(vote), headers={'Content-Type': 'application/json'})
        assert res.status_code == 201


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

if __name__ == '__main__':
    generate_member()
    try:
        unittest.main()
    finally:
        os.unlink(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))

