from bottle import route, run, template, static_file
from bottle import request, redirect, response
import gunicorn
from crawler import *
from random import shuffle, choice
import pika

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
#@route('/')
#@login_required
#def index():
#    events = get_upcoming_events()
#    data = {
#        'title' : 'BJJ events - UPCOMING IBJJF',
#        'header' : 'BJJ events',
#        "events" : events,
#    }
#    if request.get_cookie("adm"):
#        user = request.get_cookie("adm")
#        data['user'] = user
#    else:
#        redirect("/login")
#    return template('views/upcoming', data)

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

# upcoming smoothcomp events by current date
#@route('/upcoming/smoothcomp')
@route('/')
@login_required
def upcoming_smoothcomp():
    events = smoothcomp_get_upcoming_events()
    data = {
        'title' : 'BJJ events - UPCOMING SMOOTHCOMP',
        'header' : 'BJJ events',
        "events" : events,
    }
    if request.get_cookie("adm"):
        user = request.get_cookie("adm")
        data['user'] = user
    else:
        redirect("/login")
    return template('views/upcoming_smoothcomp', data)

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

@route("/kazakhstan_results/uaejjf")
@login_required
def kazakhstan():
    # e = ["183", "187", "181", "172", "164", "121", "108", "89", "44", "40", "30", "11", "5"]
    # events = [uaejjf_event_by_id(i) for i in e]
    events = uaejjf_last_events()
    #events = uaejjf_get_events_kz()
    data = {
        'title' : 'BJJ events - KAZAKHSTAN RESULTS - UAEJJF',
        'header' : 'BJJ events',
        "events" : events,
    }
    if request.get_cookie("adm"):
        user = request.get_cookie("adm")
        data['user'] = user
    else:
        redirect("/login")
    return template('views/results', data)

@route("/kazakhstan_results/smoothcomp")
@login_required
def kazakhstan_smoothcomp():
    e = ["1851", "1757", "1195", "1175", "1152", "1176", "1301", "1005", "1004"]
    events = [smoothcomp_event_by_id(i) for i in e]
    data = {
        'title' : 'BJJ events - KAZAKHSTAN RESULTS - Smoothcomp',
        'header' : 'BJJ events',
        "events" : events,
    }
    if request.get_cookie("adm"):
        user = request.get_cookie("adm")
        data['user'] = user
    else:
        redirect("/login")
    return template('views/results_smoothcomp', data)


# results KZ UAEJJF
@route("/kazakhstan_results/<event_id>")
@login_required
def kazakhstan_results(event_id):
    #results = uaejjf_event_result(event_id)
    results = uaejjf_get_results(event_id)
    data = {
        'title' : 'BJJ events - {}'.format(results.get("event")),
        'header' : 'BJJ events',
        "event" : results.get("event"),
        "athletes" : results.get("athletes"),
        "gold" : results.get("gold"),
        "silver" : results.get("silver"),
        "bronze" : results.get("bronze"),
        "last_update" : results.get("created_at"),
        "menu" : "uaejjf",
    }
    if request.get_cookie("adm"):
        user = request.get_cookie("adm")
        data['user'] = user
    else:
        redirect("/login")
    return template('views/results_athletes', data)

# results KZ UAEJJF
@route("/kazakhstan_results/smoothcomp/<event_id>")
@login_required
def kazakhstan_results_smoothcomp(event_id):
    results = smoothcomp_get_results(event_id)
    data = {
        'title' : 'BJJ events - {}'.format(results.get("event")),
        'header' : 'BJJ events',
        "event" : results.get("event"),
        "athletes" : results.get("athletes"),
        "gold" : results.get("gold"),
        "silver" : results.get("silver"),
        "bronze" : results.get("bronze"),
        "last_update" : results.get("created_at"),
        "menu" : "smoothcomp",
    }
    if request.get_cookie("adm"):
        user = request.get_cookie("adm")
        data['user'] = user
    else:
        redirect("/login")
    return template('views/results_athletes', data)

# uaejjf profile info
@route("/uaejjf/profile/<profile_id>")
@login_required
def uaejjf_profile(profile_id):
    #profile = uaejjf_parse_profile(profile_id)
    profile = uaejjf_get_profile(profile_id)
    data = {
        'title' : 'BJJ events - {}'.format(profile.get("name")),
        'header' : 'BJJ events',
        "profile" : profile,
        "menu" : "uaejjf",
    }
    if request.get_cookie("adm"):
        user = request.get_cookie("adm")
        data['user'] = user
    else:
        redirect("/login")
    return template('views/profile_uaejjf', data)

# smoothcomp profile info
@route("/smoothcomp/profile/<profile_id>")
@login_required
def smoothcomp_profile(profile_id):
    profile = smoothcomp_get_profile(profile_id)
    data = {
        'title' : 'BJJ events - {}'.format(profile.get("name")),
        'header' : 'BJJ events',
        "profile" : profile,
        "menu" : "smoothcomp",
    }
    if request.get_cookie("adm"):
        user = request.get_cookie("adm")
        data['user'] = user
    else:
        redirect("/login")
    return template('views/profile_uaejjf', data)


run(host='0.0.0.0', port=58095, server='gunicorn', workers=8)
