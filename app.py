from bottle import route, run, template, static_file
import gunicorn
from crawler import *
from random import shuffle, choice

@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')

@route('/login')
def index():
    data = {
        'title' : 'BJJ test',
        'header' : 'BJJ',
    }
    return template('views/login', data)

@route('/')
def index():
    events = get_upcoming_events()
    data = {
        'title' : 'BJJ test',
        'header' : 'BJJ',
        "events" : events,
    }
    return template('views/upcoming', data)

@route('/random')
def random():
    calendar = get_events_calendar()
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
