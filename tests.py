import os
import base64
from app import *
import unittest
import tempfile

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

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


    def test_create_poll(self):
        username = 'organizer'
        password = 'password'
        now = datetime.now()
        # Add a second to be safe.
        now = now + timedelta(seconds=1)
        tomorrow = now + timedelta(days=1)
        print tomorrow.isoformat()
        data = {}
        data['question'] = 'Is this a question?'
        data['start_time'] = now.isoformat()
        data['end_time'] = tomorrow.isoformat()
        data['select_min'] = 1
        data['select_max'] = 1
        data['options'] = ['Yes', 'No', 'Abstain']
        res = self.app.post('/polls', data=json.dumps(data), headers={'Authorization': 'Basic ' + base64.b64encode(username + ":" + password), 'Content-Type': 'application/json'})
        print res.get_data()
        assert res.status_code == 201



if __name__ == '__main__':
    try:
        unittest.main()
    finally:
        os.unlink(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))

