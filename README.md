# eVote
An API for a e-voting service developed by Eurescom.

## Users

There are three types of users.

#### Member
Members use the system to submit votes with a voting code they are provided.
Members do not have a registered user account in the system.

#### Organizer
An organizer organizes polls and performs poll management tasks. Organizers
have a registered organizer account in the system.

#### Admin
Performs administrative tasks. Admins have a registered admin account in the
system.

## Data Format
The eVote API uses the [JSend specification](http://labs.omniti.com/labs/jsend).

## Common Actions

### Voting
A member retrieves a poll by providing a voting code as an URL parameter in a
`GET` request to `/polls`.

**Example Request**

    curl -i -X GET 'localhost:5000/polls?code=zefwdxjd3n'

**Example Response**

    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 593
    Server: Werkzeug/0.10.4 Python/2.7.9
    Date: Thu, 18 Jun 2015 09:04:37 GMT

    {
      "data": {
        "poll": {
          "end_time": "2015-06-19T10:40:46.588147", 
          "id": 1, 
          "options": [
            {
              "id": 1, 
              "option": "Yes"
            }, 
            {
              "id": 2, 
              "option": "No"
            }, 
            {
              "id": 3, 
              "option": "Abstain"
            }
          ], 
          "organizer": {
            "id": 1, 
            "name": "Eurescom"
          }, 
          "question": "Are you in favor of the suggestion?", 
          "select_max": 1, 
          "select_min": 1, 
          "start_time": "2015-06-18T10:40:46.588147"
        }
      }, 
      "status": "success"
    }

A vote is submitted by sending a `POST` request to `/polls/<poll_id>/votes`.
The voting code and ids of the selected options must be provided in JSON format in the
request body.

**Example Request**

    curl -i -X POST \
    -H 'Content-Type: application/json' \
    -d '{
          "code": "zefwdxjd3n",
          "options": [2]
        }' \
    localhost:5000/polls/1/votes

**Example Response**

    HTTP/1.0 201 CREATED
    Content-Type: application/json
    Content-Length: 288
    Server: Werkzeug/0.10.4 Python/2.7.9
    Date: Thu, 18 Jun 2015 09:06:08 GMT

    {
      "data": {
        "vote": {
          "code": {
            "code": "zefwdxjd3n", 
            "id": 1
          }, 
          "id": 1, 
          "member_id": 1, 
          "options": [
            {
              "id": 2, 
              "option": "No"
            }
          ], 
          "poll_id": 1
        }
      }, 
      "status": "success"
    }

### Creating a Poll

An organizer can create a poll by sending a `POST` request to `/polls`. The
request body must include the following in JSON format:

* The poll question.
* The start time and end time in ISO 8601 format.
* The minimum and maximum number of options that can be selected.
* A list of available options.

**Example Request**

    curl -i -X POST \
    -u eurescom:password \
    -H 'Content-Type: application/json' \
    -d '{
          "question": "Are you in favor of the suggestion?",
          "start_time": "2016-06-18T10:40:46.588147",
          "end_time": "2016-06-19T10:40:46.588147",
          "select_min": 1,
          "select_max": 1,
          "options": ["Yes", "No", "Abstain"]
        }' \
    localhost:5000/polls

**Example Response**

    HTTP/1.0 201 CREATED
    Content-Type: application/json
    Content-Length: 593
    Server: Werkzeug/0.10.4 Python/2.7.9
    Date: Thu, 18 Jun 2015 09:59:28 GMT

    {
      "data": {
        "poll": {
          "end_time": "2016-06-19T10:40:46.588147", 
          "id": 2, 
          "options": [
            {
              "id": 4, 
              "option": "Yes"
            }, 
            {
              "id": 5, 
              "option": "No"
            }, 
            {
              "id": 6, 
              "option": "Abstain"
            }
          ], 
          "organizer": {
            "id": 1, 
            "name": "Eurescom"
          }, 
          "question": "Are you in favor of the suggestion?", 
          "select_max": 1, 
          "select_min": 1, 
          "start_time": "2016-06-18T10:40:46.588147"
        }
      }, 
      "status": "success"
    }

### Creating a member

An organizer can create a member by sending a `POST` request to `/members`. The
request body must contain the following in JSON format:

* The name of the member organization.
* The group the member belongs to.
* A list of contact persons for the member organization.

Each contact person must contain the following fields:

* The name of the contact person.
* The contact person's email address.

**Example Request**

    curl -i -X POST \
    -u eurescom:password \
    -H 'Content-Type: application/json' \
    -d '{
          "name": "Siminn",
          "group": "SomeGroup",
          "contacts": [ 
            { 
              "name": "Saemi",
              "email": "saemi@siminn.is"
            },
            {
              "name": "Thor",
              "email": "thor@siminn.is"
            }
          ]
        }' \
    localhost:5000/members


**Example Response**

    HTTP/1.0 201 CREATED
    Content-Type: application/json
    Content-Length: 373
    Server: Werkzeug/0.10.4 Python/2.7.9
    Date: Thu, 18 Jun 2015 12:00:23 GMT

    {
      "data": {
        "member": {
          "contacts": [
            {
              "email": "saemi@siminn.is", 
              "id": 6, 
              "name": "Saemi"
            }, 
            {
              "email": "thor@siminn.is", 
              "id": 7, 
              "name": "Thor"
            }
          ], 
          "group": "SomeGroup", 
          "id": 2, 
          "name": "Siminn"
        }
      }, 
      "status": "success"
    }

### Generating Voting Codes

An organizer can create voting codes by sending a `POST` request to
`/poll/<pollId>/codes`. The request body must contain a list of member ids in
JSON format.

**Example Request**

    curl -i -X POST \
    -u eurescom:password \
    -H 'Content-Type: application/json' \
    -d '{
          "member_ids": [1, 2, 3]
        }' \
    localhost:5000/polls/1/codes

**Example Response**

    HTTP/1.0 201 CREATED
    Content-Type: application/json
    Content-Length: 257
    Server: Werkzeug/0.10.4 Python/2.7.9
    Date: Thu, 18 Jun 2015 13:15:46 GMT

    {
      "data": {
        "codes": [
          {
            "code": "8j6ughiash", 
            "id": 1
          }, 
          {
            "code": "upgjgu19vs", 
            "id": 2
          }, 
          {
            "code": "pb1ub86ssj", 
            "id": 3
          }
        ]
      }, 
      "status": "success"
    }

