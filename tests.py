import os
import base64
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
        now = datetime.now()
        # Add a second to be safe.
        now = now + timedelta(seconds=1)

        tomorrow = now + timedelta(days=1)

        data = {}
        data['question'] = 'Is this a question?'
        data['start_time'] = now.isoformat()
        data['end_time'] = tomorrow.isoformat()
        data['select_min'] = 1
        data['select_max'] = 1
        data['options'] = ['Yes', 'No', 'Abstain']

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
        print res_data
        js = json.loads(res_data)
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
        data = {}
        data['name'] = 'Siminn'
        data['group'] = 'Telekom'
        data['contacts'] = [{'name': 'Saemi', 'email': 'saemi@siminn.is'}, {'name': 'Thor', 'email': 'thor@siminn.is'}]

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

        # Compare the data.
        for key in data:
            if key == 'contacts':
                assert len(data['contacts']) == len(member['contacts'])
                for contact in member['contacts']:
                    assert {'name': contact['name'], 'email': contact['email']} in data['contacts']
            else:
                assert member[key] == data[key]

if __name__ == '__main__':
    try:
        unittest.main()
    finally:
        os.unlink(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))

