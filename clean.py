from app import *

print 'Dropping tables'
db.drop_all()

print 'Creating tables'
db.create_all()

print 'Adding users and organizer'
admin = User('admin', 'password', True)
db.session.add(admin)

user = User('organizer', 'password')
db.session.add(user)
organizer = Organizer('Eurescom')
organizer.user = user
db.session.add(organizer)

print 'Committing changes'
db.session.commit()

print 'Cleanup done!'
