from bottle import route, run, template, static_file
from bottle import request, redirect, response
import gunicorn
from crawler import *
from random import shuffle, choice

def check_user(login, pw):
    h = hashlib.sha256("{}:{}".format(login, pw).encode()).hexdigest()
    secret = '397ad1751b7dc48d6c7e039b28d7f58994ae4bbd281ae922ace6b25636ebc6bf'
    if h == secret:
        return True
    return False

# login required decorator (admin)
def login_required(fn):
    def check_uid(**kwargs):
        cookie_uid = request.get_cookie('adm', secret='bjj')
        if cookie_uid:
            return fn(**kwargs)
        else:
            redirect("/login")
    return check_uid

@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')

# login page
@route('/login')
def login():
    data = {
        'title' : 'BJJ test',
        'header' : 'BJJ events',
    }
    return template('views/login', data)

# login logic
@route('/login', method = 'POST')
def login_logic():
    login = request.forms.get("email")
    pw = request.forms.get("password")
    if check_user(login, pw):
        response.set_cookie("adm", login, secret='bjj', path='/', max_age=3600)
        data = {
            'title' : 'BJJ test',
            'header' : 'BJJ events',
            'user' : login,
        }
        redirect('/')
    else:
        redirect('/login')

# logout
@route('/logout')
def logout():
    response.delete_cookie("adm", path='/')
    return redirect('/login')

# upcoming events by current date
@route('/')
@login_required
def index():
    events = get_upcoming_events()
    data = {
        'title' : 'BJJ events - UPCOMING IBJJF',
        'header' : 'BJJ events',
        "events" : events,
    }
    if request.get_cookie("adm"):
        user = request.get_cookie("adm")
        data['user'] = user
    else:
        redirect("/login")
    return template('views/upcoming', data)

# upcoming uaejjf events by current date
@route('/upcoming/uaejjf')
@login_required
def upcoming_uaejjf():
    events = uaejjf_get_upcoming_events()
    data = {
        'title' : 'BJJ events - UPCOMING UAEJJF',
        'header' : 'BJJ events',
        "events" : events,
    }
    if request.get_cookie("adm"):
        user = request.get_cookie("adm")
        data['user'] = user
    else:
        redirect("/login")
    return template('views/upcoming_uaejjf', data)

# upcoming all events by current date
@route('/upcoming/all')
@login_required
def upcoming_all():
    events = get_upcoming_all()
    data = {
        'title' : 'BJJ events - UPCOMING EVENTS',
        'header' : 'BJJ events',
        "events" : events,
    }
    if request.get_cookie("adm"):
        user = request.get_cookie("adm")
        data['user'] = user
    else:
        redirect("/login")
    return template('views/upcoming_all', data)


# random event
@route('/random')
@login_required
def random():
    calendar = get_events_calendar()
    shuffle(calendar)
    events = [get_event_info(choice(calendar))]
    data = {
        'title' : 'BJJ events - RANDOM EVENT',
        'header' : 'BJJ events',
        "events" : events,
    }
    if request.get_cookie("adm"):
        user = request.get_cookie("adm")
        data['user'] = user
    else:
        redirect("/login")
    return template('views/random', data)

# all events from db
@route('/all')
@login_required
def all():
    events = get_events(size=25, offset = 0)
    data = {
        'title' : 'BJJ events - ALL',
        'header' : 'BJJ events',
        "events" : events,
    }
    if request.get_cookie("adm"):
        user = request.get_cookie("adm")
        data['user'] = user
    else:
        redirect("/login")
    return template('views/all', data) 

@route("/kazakhstan_results")
@login_required
def kazakhstan():
    events = [uaejjf_event_by_id(i) for i in ["187", "172", "108", "5"]]
    #events = uaejjf_last_events()
    data = {
        'title' : 'BJJ events - KAZAKHSTAN RESULTS',
        'header' : 'BJJ events',
        "events" : events,
    }
    if request.get_cookie("adm"):
        user = request.get_cookie("adm")
        data['user'] = user
    else:
        redirect("/login")
    return template('views/results', data)

# results KZ
@route("/kazakhstan_results/<event_id>")
@login_required
def kazakhstan_results(event_id):
    results = uaejjf_event_result(event_id)
    data = {
        'title' : 'BJJ events - KAZAKHSTAN RESULTS',
        'header' : 'BJJ events',
        "event" : results.get("event"),
        "athletes" : results.get("athletes"),
        "gold" : results.get("gold"),
        "silver" : results.get("silver"),
        "bronze" : results.get("bronze"),
    }
    if request.get_cookie("adm"):
        user = request.get_cookie("adm")
        data['user'] = user
    else:
        redirect("/login")
    return template('views/results_athletes', data)

run(host='10.10.1.143', port=58095, server='gunicorn', workers=4)
