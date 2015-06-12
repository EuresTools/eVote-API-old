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

    try:
        poll.select_min = int(json['select_min'])
        if poll.select_min < 0:
            error['select_min'] = 'The minimum number of selections cannot be negative'
    except ValueError, e:
        error['select_min'] = 'The minimum number of selections must be an integer'

    try:
        poll.select_max = int(json['select_max'])
        if poll.select_max < 1:
            error['select_max'] = 'The maximum number of selections must be greater than 0'
    except ValueError, e:
        error['select_max'] = 'The maximum number of selections must be an integer'

    try:
        poll.start_time = iso8601.parse_date(json['start_time'])

        # Avoid timezone hell for now...
        poll.start_time = poll.start_time.replace(tzinfo=None)

    except iso8601.ParseError, e:
        error['start_time'] = 'The start time must be ISO 8601 formatted'

    try:
        poll.end_time = iso8601.parse_date(json['end_time'])

        # Avoid timezone hell for now...
        poll.end_time = poll.end_time.replace(tzinfo=None)
    except iso8601.ParseError, e:
        error['end_time'] = 'The end time must be ISO 8601 formatted'

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
        print 'Value error on options'
        error['options'] = 'The options must be a list of valid strings'


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

    success = len(error) == 0
    if not success:
        return None, error
    return poll, None
