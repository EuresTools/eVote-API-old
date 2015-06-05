# eVote REST API

This document serves as a description of the functional requirements of the
e-voting API.

## Users and Roles

#### Member

A member is registered in the system by an organizer or an admin.  
A member belongs to some organizer.  
A member is not directly identified by the system.

A member can

* Submit a voting code and get back a poll.
* Submit a vote to a poll.

#### Organizer

An organizer is registered in the system by an admin.  
An organizer is identified by username and password.

An organizer can

* Register a new member in the system.
* Create a new poll.
* Add members to a given poll.
* Get a list of members managed by the organizer.
* Get details about a given member.
* Get a list of polls organized by the organizer.
* Get details for a given poll.
* Get all votes for a given poll.
* Get details for a given vote.
* Void a given vote.
* Send an email to every member in a given poll.


#### Admin

An admin is registered in the system by another admin.  
An admin is identified by username and password.

An admin can

* Create and delete organizers.
* Create and delete other admins.


## Resources

Here we list required entities and their attributes.

#### Member

* Organizer ID.
* Organization name.
* Stakeholder group.
* List of contact persons.

#### Contact

* Member ID.
* Email address.

#### Poll

* Organizer ID.
* List of members.
* Start datetime.
* End datetime.
* Options.
* Min options selected.
* Max options selected.

#### Vote

* Voting code.
* Poll ID.
* Options.


## API Endpoints

`GET /polls`  
Returns a list of polls. If the `code` parameter is specified, a unique poll
for that code is returned. If the `code` parameter is not specified, organizer
or admin credentials are required. An organizer will only receive the polls
owned by the organizer.

`POST /polls`  
Creates and returns a new poll. Organizer or admin credentials are required.

`GET /polls/:id`  
Returns a specific poll with the provided id. Organizer or admin credentials
are required.

`PUT /polls/:id`  
Updates a specific poll with the provided id. Organizer or admin credentials
are required.

`DELETE /polls/:id`  
Removes a specific poll with the provided id. Organizer or admin credentials
are required.

`GET /polls/:id/votes`  
Returns a list of votes in the given poll. Organizer or admin credentials are
required.

`POST /polls/:id/votes`  
Creates and returns a vote in the given poll. The `code` parameter is required.

`GET /polls/:id/votes/:id`  
Returns a vote in the given poll with the prodided id. Organizer or admin
credentials are required.

`DELETE /polls/:id/votes/:id`  
Voids the vote with the provided id. Organizer or admin credentials are
required.

`GET /members`  
Returns a list of members. Organizer or admin credentials required.

`POST /members`  
Creates and returns a new member. Organizer or admin credentials required.

`GET /members/:id`  
Returns a member with the given id. Organizer or admin credentials required.

`PUT /members/:id`  
Updates a member with the given id. Organizer or admin credentials required.

`DELETE /members/:id`  
Deletes a member with the given id. Organizer or admin credentials required.


<!--## Thoughts-->

<!--* If an organizer voids a vote the member should be notified and asked to-->
  <!--confirm the invalidation.-->
