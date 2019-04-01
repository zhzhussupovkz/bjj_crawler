from bottle import route, run, template, static_file
import gunicorn
from crawler import *
from random import shuffle

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
    return template('views/random', data)


run(host='localhost', port=8090, server='gunicorn', workers=4)