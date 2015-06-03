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
* Get a list of polls organized by the organizer.
* Get details for a given poll.
* Get all votes for a given poll.
* Get details for a given vote.
* Void a given vote.

#### Admin

An admin is registered in the system by another admin.  
An admin is identified by username and password.

An admin can

* Do a lot of stuff.


## Thoughts

* If an organizer voids a vote the voter should be notified and asked to
  confirm the invalidation.
