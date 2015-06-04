# eVote REST API

This document serves as a description of the functional requirements of the
e-voting API.

## Users and Roles

#### Voter

A voter is registered in the system by an organizer or an admin.  
A voter belongs to some organizer.  
A voter is identified by a voting code issued to that voter for each poll.

A voter can

* Submit a voting code and get back a poll.
* Submit a vote to a poll.

#### Organizer

An organizer is registered in the system by an admin.  
An organizer is identified by username and password.

An organizer can

* Register a new voter in the system.
* Create a new poll.
* Add voters to a given poll.
* Get a list of voters owned by the organizer.
* Get details about a given voter.
* Get a list of polls organized by the organizer.
* Get details for a given poll.
* Get all votes for a given poll.
* Get details for a given vote.
* Void a given vote.
* Send an email to every voter in a given poll.


#### Admin

An admin is registered in the system by another admin.  
An admin is identified by username and password.

An admin can

* Create and delete organizers.
* Create and delete other admins.
* Assign or unassign roles to users.


## Entities

Here we list required entities and their attributes.

#### User

* List of roles.
* Username.
* Password.

#### Voter

* Organizer ID.
* Organization name.
* Stakeholder group.
* List of contact persons.

#### Contact Person

* Voter ID.
* Email address.

#### Poll

* Organizer ID.
* List of voters.
* Start datetime.
* End datetime.
* Options.
* Min options selected.
* Max options selected.

#### Vote

* Voting code.
* Poll ID.
* Options.


## Thoughts

* If an organizer voids a vote the voter should be notified and asked to
  confirm the invalidation.
