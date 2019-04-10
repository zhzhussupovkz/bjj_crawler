from bottle import route, run, template, static_file
import gunicorn
from crawler import *
from random import shuffle, choice

@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')

@route('/')
def index():
    calendar = get_calendar()
    events = [get_event_info(i) for i in calendar[3:6]]
    data = {
        'title' : 'BJJ test',
        'header' : 'BJJ',
        "events" : events,
    }
    return template('views/index', data)

@route('/upcoming')
def upcoming():
    calendar = get_calendar()
    shuffle(calendar)
    events = [get_event_info(i) for i in calendar[3:6]]
    data = {
        'title' : 'BJJ test',
        'header' : 'BJJ',
        "events" : events,
    }
    return template('views/upcoming', data)

@route('/random')
def random():
    calendar = get_calendar()
    shuffle(calendar)
    events = [get_event_info(choice(calendar))]
    data = {
        'title' : 'BJJ random event',
        'header' : 'BJJ',
        "events" : events,
    }
    return template('views/random', data)

@route('/all')
def all():
    events = get_events(size=25, offset = 0)
    data = {
        'title' : 'BJJ test',
        'header' : 'BJJ',
        "events" : events,
    }
    return template('views/all', data)

   

run(host='10.10.1.143', port=58095, server='gunicorn', workers=4)
