import models
import iso8601
import pytz
from datetime import datetime, timedelta

# Returns a 2-tuple.
# Either a poll object and None or None and a dictionary of error messages.
def parse_poll(json):
    poll = models.Poll()
    # Put all errors in a dictionary to return to the user.
    error = {}
    try:
        poll.question = str(json['question'])
    except ValueError, e:
        error['question'] = 'The question must be a valid string'
    except KeyError, e:
        error['question'] = 'The \'question\' field is required'

    try:
        poll.select_min = int(json['select_min'])
        if poll.select_min < 0:
            error['select_min'] = 'The minimum number of selections cannot be negative'
    except ValueError, e:
        error['select_min'] = 'The minimum number of selections must be an integer'
    except KeyError, e:
        error['select_min'] = 'The \'select_min\' field is required'

    try:
        poll.select_max = int(json['select_max'])
        if poll.select_max < 1:
            error['select_max'] = 'The maximum number of selections must be greater than 0'
    except ValueError, e:
        error['select_max'] = 'The maximum number of selections must be an integer'
    except KeyError, e:
        error['select_max'] = 'The \'select_max\' field is required'

    try:
        poll.start_time = iso8601.parse_date(json['start_time'])

        # Avoid timezone hell for now...
        poll.start_time = poll.start_time.replace(tzinfo=None)

    except iso8601.ParseError, e:
        error['start_time'] = 'The start time must be ISO 8601 formatted'
    except KeyError, e:
        error['start_time'] = 'The \'start_time\' field is required'

    try:
        poll.end_time = iso8601.parse_date(json['end_time'])

        # Avoid timezone hell for now...
        poll.end_time = poll.end_time.replace(tzinfo=None)
    except iso8601.ParseError, e:
        error['end_time'] = 'The end time must be ISO 8601 formatted'
    except KeyError, e:
        error['end_time'] = 'The \'end_time\' field is required'

    try:
        options = json['options']
        if not isinstance(options, list):
            error['options'] = 'Options must be provided in a list'
        elif len(options) < 2:
            error['options'] = 'There must be at least 2 options'

        # Check for duplicate options.
        elif len(options) != len(set(options)):
            error['options'] = 'The options must be unique'
        else:
            for o in options:
                string = str(o)
                option = models.Option(string)
                option.poll = poll
    except ValueError, e:
        error['options'] = 'The options must be a list of valid strings'
    except KeyError, e:
        error['options'] = 'The \'options\' field is required'


    now = datetime.now()
    now = now.replace(tzinfo=None)
    # Round down to last second.
    now = now - timedelta(minutes=0, seconds=0, microseconds=now.microsecond)

    # Validate the start time.
    if poll.start_time:
        if now > poll.start_time:
            error['start_time'] = 'The vote cannot start in the past'

    # Validate the end time.
    if poll.end_time:
        if now > poll.end_time:
            error['end_time'] = 'The vote cannot end in the past'

    # Validate the relationship between the start and end times.
    if poll.start_time and poll.end_time:
        if poll.start_time >= poll.end_time:
            if 'start_time' not in error:
                error['start_time'] = 'The poll must start before it ends'
            if 'end_time' not in error:
                error['end_time'] = 'The poll cannot end before it starts.'

    # Validate the relationship between select_min and select_max.
    if not 'select_min' in error and not 'select_max' in error:
        if poll.select_min > poll.select_max:
            error['select_min'] = 'The minimum number of selections cannot be greater than the maximum'
            error['select_max'] = 'The maximum number of selections cannot be less than the minimum'

    if error:
        return None, error
    return poll, None

# The caller must also provide the appropriate poll object for validation.
def parse_vote(json, poll):
    vote = models.Vote()
    vote.time = datetime.now().replace(tzinfo=None)
    # Put all errors in a dictionary to return to the user.
    error = {}

    # Check if the poll is open.
    #if vote.time < poll.start_time:
         #error['message'] = 'This poll is not open yet'
    #elif vote.time > poll.end_time:
         #error['message'] = 'This poll is no longer open'

    # Don't provide further error messages if the poll is not open.
    #if error:
        #return None, error

    try:
        vote_code = str(json['code'])
    except ValueError, e:
        error['code'] = 'The voting code must be a valid string'
    except KeyError, e:
        error['code'] = 'The \'code\' parameter is required'

    code = None
    if 'code' not in error:
        try:
            code = models.Code.query.filter_by(code=vote_code).one()
        except NoResultFound, e:
            error['code'] = 'This voting code is invalid'
        except MultipleResultsFound, e:
            error['code'] = 'There is an unknown problem with this voting code'

    if code:
        # Check if the code is for this poll.
        if code.poll != poll:
            error['code'] = 'This voting code is invalid'
        elif code.vote:
            error['code'] = 'This voting code has already been used'

    # Don't provide further error messages if there is a problem with the code.
    if error:
        return None, error
    
    vote.code = code
    vote.member = code.member
    vote.poll = code.poll

    try:
        options = json['options']
        if not isinstance(options, list):
            error['options'] = 'Options must be provided in a list'
        elif len(options) < poll.select_min:
            error['options'] = 'There must be at least %d options' % (poll.select_min)
        elif len(options) < poll.select_max:
            error['options'] = 'There can at most be %d options' % (poll.select_max)

        # Check for duplicate options.
        elif len(options) != len(set(options)):
            error['options'] = 'The options must be unique'
        else:
            for o in options:
                option_id = int(o)
                try:
                    option = models.Option.query.filter_by(id=option_id, poll=poll).one()
                    vote.options.append(option)
                except (NoResultFound, MultipleResultsFound), e:
                    error['options'] = 'One or more options are invalid'
    except ValueError, e:
        error['options'] = 'The options must be a list of valid integers'
    except KeyError, e:
        error['options'] = 'The \'options\' parameter is required'

    if error:
        return None, error
    return vote, None

def parse_member(json):
    member = models.Member()
    error = {}
    try:
        member.name = str(json['name'])
    except ValueError, e:
        error['name'] = 'Name must be a valid string'
    except KeyError, e:
        error['name'] = 'The \'name\' field is required'

    try:
        member.group = str(json['group'])
    except ValueError, e:
        error['group'] = 'Group must be a valid string'
    except KeyError, e:
        error['group'] = 'The \'group\' field is required'

    try:
        contacts = json['contacts']
        if not isinstance(options, list):
            error['contacts'] = 'Contacts must be provided in a list'
        elif not contacts:
            error['contacts'] = 'At least one contact must be specified'
        else:
            emails = set()
            for c in contacts:
                contact = models.Contact()
                contact.member = member
                try:
                    contact.name = str(c['name'])
                except ValueError, e:
                    error['contacts'] = 'The contact names must be valid strings'
                    break
                except KeyError, e:
                    error['contacts'] = 'The \'name\' field is required for each contact'
                    break
                try:
                    contact.email = str(c['email'])
                    # TODO: Validate email format
                    if contact.email in emails:
                        error['contacts'] = 'The contact emails must be unique'
                        break
                    emails.add(contact.email)
                except ValueError, e:
                    error['contacts'] = 'The contact emails must be valid strings'
                    break
                except KeyError, e:
                    error['contacts'] = 'The \'email\' field is required for each contact'
                    break
    except KeyError, e:
        error['contacts'] = 'The \'contacts\' field is required'

    if error:
        return None, error
    return member, None

def parse_codes(json, organizer):
    codes = []
    error = {}
    poll = None
    try:
        poll_id = int(json['poll_id'])
        poll = models.Member.filter_by(id=poll_id, organizer=organizer).one()
    except ValueError, e:
        error['poll_id'] = 'poll_id must be a valid integer'
    except KeyError, e:
        error['poll_id'] = 'The \'poll_id\' field is required'
    except (NoResultFound, MultipleResultsFound), e:
        error['poll_id'] = 'Invalid poll id'


    try:
        member_ids = json['member_ids']
        if not isinstance(member_ids, list):
            error['member_ids'] = 'Member ids must be provided in a list'
        elif not member_ids:
            error['member_ids'] = 'At least one member id must be specified'
        else:
            for member_id_str in member_ids:
                member_id = int(member_id_str)
                member = models.Member.filter_by(id=member_id, organizer=organizer).one()
                code = models.Code()
                code.poll = poll
                code.member = member

    except ValueError, e:
        error['member_id'] = 'The member_ids must be a valid integer'
    except KeyError, e:
        error['member_id'] = 'The \'member_id\' field is required'
    except (NoResultFound, MultipleResultsFound), e:
        error['member_id'] = 'At least one member id is invalid'

    if error:
        return None, error
    return codes, None

