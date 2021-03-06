import json
import requests
import lxml.html
import logging
from elasticsearch import Elasticsearch
import hashlib
import time, datetime
import base64
import random
import dateparser
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s: %(levelname)s %(message)s')
es = Elasticsearch(["192.168.0.19:11200", "192.168.0.2:11200", "192.168.0.5:11200"], maxsize=25)

def get_proxy():
    # proxy_url = 'https://api.getproxylist.com/proxy?' \
    #             'apiKey=ffe605ca03ce2bc63433ce44032fed59b13a448b' \
    #             '&allowsHttps=1' \
    #             #'&lastTested=600' \
    #             #'&allowsPost=1' \
    #             #'&allowsCookies=1' \
    #             #'&allowsCustomHeaders=1' \
    #             #'&allowsUserAgentHeader=1' \
    #             #'&allowsRefererHeader=1' \
    #             #'&[]anonymity=high'

    # r = requests.get(proxy_url)
    # if r.ok:
    #     proxy = json.loads(r.text)
    #     proxy = str(proxy['ip']) + ':' + str(proxy['port'])
    #     proxies = {"http": "http://" + proxy, "https": "https://" + proxy}
    #     return proxies

    proxies = {
        'http': 'http://rinat94:Z0x3MrS@185.117.155.238:65233',
        'https': 'https://rinat94:Z0x3MrS@185.117.155.238:65233'
        }

    return proxies

# get events from calendar
def get_events_calendar():
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    s = requests.session()
    proxies = get_proxy()
    r = s.get(url = "https://ibjjf.com/championships/calendar/", headers = headers) #, proxies = proxies)
    if r.ok:
        calendar = r.text
        tree = lxml.html.fromstring(calendar)
        links = tree.xpath(".//div[contains(@id, 'content')]//table//tr//td//a/@href")
        links = list(filter(lambda i: "ibjjf.com" in i, links))
        return links
    return []

# get events uaejjf
def uaejjf_get_calendar():
    result = []
    proxies = get_proxy()
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    s = requests.session()
    # r = s.get(url = "https://events.uaejjf.org/en/federation/1/events", headers = headers)
    r = s.get(url = "https://ajptour.com/en/federation/1/events", headers = headers, proxies = proxies)
    if r.ok:
        calendar = r.text
        tree = lxml.html.fromstring(calendar)
        events = tree.xpath(".//section[contains(@id, 'upcoming')]//div[contains(@class, 'event-bg')]//div[contains(@class, 'content')]")
        for event in events:
            link = event.xpath(".//a/@href")
            link = link[0] if link and "ajptour.com" in link[0] else ''
            date = event.xpath(".//span[contains(@class, 'tag')]")
            date = date[0].text_content().strip() if date else ''
            result.append((link, date))
        #links = list(filter(lambda i: "uaejjf.org" in i, links))
        return result
    return []

# smoothcomp get events
def smoothcomp_events(period = "upcoming"):
    result = []
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    s = requests.session()
    r = s.get(url = "https://smoothcomp.com/en/events/{}".format(period), headers = headers)
    if r.ok:
        calendar = r.text
        events = re.search("var events(.*)", calendar)
        if events:
            events = events.group(1).strip().strip("=").strip()
            events_list = json.loads(events)

            for event in events_list:
                result.append((event.get("url"), event.get("eventPeriod")))
    return result

# get uaejjf past events
def uaejjf_past_events():
    result = []
    proxies = get_proxy()
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    s = requests.session()
    # r = s.get(url = "https://events.uaejjf.org/en/federation/1/events", headers = headers)
    r = s.get(url = "https://ajptour.com/en/federation/1/events", headers = headers, proxies = proxies)
    if r.ok:
        calendar = r.text
        tree = lxml.html.fromstring(calendar)
        events = tree.xpath(".//section[contains(@id, 'past-events')]//div[contains(@class, 'event-card')]//div[contains(@class, 'content')]")
        for event in events:
            link = event.xpath("..//a/@href")
            link = link[0] if link and "ajptour.com" in link[0] else ''
            date = event.xpath(".//span[contains(@class, 'tag')]")
            date = date[0].text_content().strip() if date else ''
            result.append((link, date))
        #links = list(filter(lambda i: "uaejjf.org" in i, links))
        return result
    return []
    

# parse current event by link
def get_event_info(link):
    if link.startswith("//ibjjf.com"):
        link = "https:" + link
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    r = requests.get(url = link, headers = headers, proxies = get_proxy())
    if r.ok:
        event_info = {}
        event = r.text
        tree = lxml.html.fromstring(event)

        event_info['url'] = link

        img = tree.xpath(".//div[@id='container']//ul[contains(@id,'banner')]//img/@src")
        event_info['img'] = img[0] if img else ""

        name = tree.xpath(".//div[contains(@id, 'post')]//h2")
        event_info['name'] = name[0].text_content() if name else "not found"

        date = tree.xpath(".//div[contains(@id, 'post')]//abbr")
        date_str = date[0].text_content().strip("*") if date else "not found"
        date_str = date_str.replace(" and", ",").replace("and ", ",").replace(" &", ",").replace("& ", ",")
        date_str = date_str.replace(" *", ",").replace("* ", ",").split(" ")
        date_str = list(filter(lambda d: (d != ","), date_str))
        date_str = list(filter(None, date_str))
        df = ["{} {} {}".format(date_str[0], i, date_str[-1]) for i in date_str[1:-1]]
        dates = [dateparser.parse(i) for i in df]
        dates = list(filter(None, dates))
        event_info['date'] = list(set(dates))

        relevant_dates = tree.xpath(".//div[contains(@id, 'championships-dates')]//ul//li//abbr")
        relevant_dates = [i.text_content().strip("\n").strip("\t").replace("\t", "") for i in relevant_dates] if relevant_dates else []
        event_info["relevant_dates"] = relevant_dates

        location = tree.xpath(".//div[contains(@id, 'post-info')]//address")
        event_info['location'] = location[0].text_content().strip() if location else "not found"

        info = tree.xpath(".//div[contains(@id, 'post-info')]//span")
        info = [i.text_content().strip().replace("\t", "").replace("\n", " ").replace("\r", "") for i in info] if info else []
        event_info["info"] = list(filter(None, info))

        divisions = tree.xpath(".//div[contains(@id, 'divisions')]//table//tbody//tr//td")
        event_info['divisions'] = [t.text_content() for t in divisions] if divisions else []

        ranking = tree.xpath(".//div[contains(@id, 'post-info')]//span//img[contains(@class, 'wp-image')]/@src")
        event_info['ranking'] = ranking[-1] if ranking else ""

        if event_info['ranking'].startswith("//ibjjf.com"):
            event_info['ranking'] = "https:" + event_info.get("ranking")

        return event_info
    return {}

# get uaejjf event info
def uaejjf_get_event(e):
    link, date = e
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0'
    }
    r = requests.get(url = link, headers = headers)
    if r.ok:
        event_info = {}

        event = r.text
        tree = lxml.html.fromstring(event)

        event_info['url'] = link

        img = tree.xpath(".//div[contains(@class, 'cover-image')]//img/@src")
        event_info['img'] = img[0] if img else ""

        name = tree.xpath(".//title")
        event_info['name'] = name[0].text_content().strip().replace("\n", "") if name else "not found"
        
        date_y = date.split(" ")
        if len(date_y) == 3:
            df = date.split("-")[:1]
        elif len(date_y) == 2:
            df = date.split("-")[:1]
            df = [str(datetime.datetime.now().year) + " " + i for i in df]

        dates = [datetime.datetime.strptime(i, "%Y %B %d") for i in df]
        dates = list(filter(None, dates))
        event_info['date'] = list(set(dates))

        event_info["relevant_dates"] = []

        location = tree.xpath(".//div[contains(@class, 'location')]")
        event_info['location'] = location[0].text_content().strip() if location else "not found"

        info = tree.xpath(".//div[contains(@class, 'information')]")
        info = [i.text_content().strip().replace("\t", " ").replace("\n", " ").replace("\r", " ") for i in info] if info else []
        event_info["info"] = list(filter(None, info))

        entries = tree.xpath(".//div[contains(@class, 'panel-inverted')]//ul")
        entries = entries[-1].xpath(".//li")
        entries = [i.text_content().strip().replace("\n", " ") for i in entries] if entries else []
        event_info['entries'] = entries

        event_info["register_link"] = "{}/register".format(link.strip("/"))
        event_info["event_id"] = link.split("/")[-1]

        return event_info
        
    return {}

# get smoothcomp event info
def smoothcomp_get_event(e):
    link, date = e
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0'
    }
    r = requests.get(url = link, headers = headers)
    if r.ok:
        event_info = {}

        event = r.text
        tree = lxml.html.fromstring(event)

        event_info['url'] = link

        img = tree.xpath(".//div[contains(@class, 'cover-image')]//img/@src")
        event_info['img'] = img[0] if img else ""

        name = tree.xpath(".//title")
        event_info['name'] = name[0].text_content().strip().replace("\n", "") if name else "not found"
        
        date_y = date.split(" ")
        if len(date_y) == 3:
            df = date.split("-")[:1]
        elif len(date_y) == 2:
            df = date.split("-")[:1]
            df = [str(datetime.datetime.now().year) + " " + i for i in df]

        dates = [datetime.datetime.strptime(i, "%Y %B %d") for i in df]
        dates = list(filter(None, dates))
        event_info['date'] = list(set(dates))

        location = tree.xpath(".//div[contains(@class, 'location')]")
        event_info['location'] = location[0].text_content().strip() if location else "not found"

        info = tree.xpath(".//div[contains(@class, 'information')]")
        info = [i.text_content().strip().replace("\t", " ").replace("\n", " ").replace("\r", " ") for i in info] if info else []
        event_info["info"] = list(filter(None, info))

        entries = tree.xpath(".//div[contains(@class, 'panel-inverted')]//ul")
        entries = entries[-1].xpath(".//li")
        entries = [i.text_content().strip().replace("\n", " ") for i in entries] if entries else []
        event_info['entries'] = entries

        event_info["register_link"] = "{}/register".format(link.strip("/"))
        event_info["event_id"] = link.split("/")[-1]

        copyright = tree.xpath(".//div[contains(@class, 'footer')]//div")
        event_info['copyright'] = copyright[0].text_content().strip().replace("\n", "") if copyright else ""

        return event_info
        
    return {}
    
# save event to db
def save_to_db(event):
    try:
        # save image
        r = requests.get(event.get("img"))
        if r.ok:
            img = str(base64.b64encode(r.content).decode("utf-8"))
        else:
            img = ""

        # save ranking image
        r = requests.get(event.get("ranking"))
        if r.ok:
            ranking_img = str(base64.b64encode(r.content).decode("utf-8"))
        else:
            ranking_img = ""
    
        doc = {   
            "url" : event.get("url"),
            "img" : img,
            "ranking" : ranking_img,
            "name" : event.get("name"),
            "date" : [i.strftime("%Y-%m-%d") for i in event.get("date")],
            "relevant_dates" : event.get("relevant_dates"),
            "location" : event.get("location"),
            "info" : event.get("info"),
            "created_at" : datetime.datetime.now().strftime("%Y-%m-%d"),
            "additional_props" : {"divisions" : event.get("divisions")},
        }
        doc_id = hashlib.sha256((event["url"] + ",".join(doc.get("date"))).encode()).hexdigest()
        doc["id"] = doc_id
        res = es.index(index = "bjj_test", doc_type = 'event', id = doc.get("id"), body = doc)
        logging.info(res)        
    except Exception as e:
        logging.error(str(e))

def uaejjf_save(event):
    try:
        if not event.get("img").startswith("https://ajptour.com"):
            event['img'] = "https://ajptour.com" + event.get("img")
        if event.get("img").startswith("//ajptour"):
            event['img'] = "https:" + event.get("img")
        # save image
        r = requests.get(event.get("img"))
        if r.ok:
            img = str(base64.b64encode(r.content).decode("utf-8"))
        else:
            img = ""
    
        doc = {
            "id" : event.get("event_id"),   
            "url" : event.get("url"),
            "img" : img,
            "entries" : event.get("entries"),
            "name" : event.get("name"),
            "date" : [i.strftime("%Y-%m-%d") for i in event.get("date")],
            "relevant_dates" : event.get("relevant_dates"),
            "register_link" : event.get("register_link"),
            "location" : event.get("location"),
            "info" : event.get("info"),
            "created_at" : datetime.datetime.now().strftime("%Y-%m-%d"),
            "event_id" : event.get("event_id"),
        }
        #doc_id = hashlib.sha256((event["url"] + ",".join(doc.get("date"))).encode()).hexdigest()
        #doc["id"] = doc_id
        res = es.index(index = "uaejjf_test", doc_type = 'event', id = doc.get("id"), body = doc)
        logging.info(res)        
    except Exception as e:
        logging.error(str(e))

# smoothcomp save
def smoothcomp_save(event):
    try:
        if not event.get("img").startswith("https://smoothcomp.com"):
            event['img'] = "https://smoothcomp.com" + event.get("img")
        if event.get("img").startswith("//smoothcomp.com"):
            event['img'] = "https:" + event.get("img")

        # save image
        r = requests.get(event.get("img"))
        if r.ok:
            img = str(base64.b64encode(r.content).decode("utf-8"))
        else:
            img = ""
    
        doc = {
            "id" : event.get("event_id"),
            "url" : event.get("url"),
            "img" : img,
            "entries" : event.get("entries"),
            "name" : event.get("name"),
            #"date" : [int(i.timestamp()) for i in event.get("date")], #[i.strftime("%Y-%m-%d") for i in event.get("date")],
            "date" : [i.strftime("%Y-%m-%d") for i in event.get("date")],
            "copyright" : event.get("copyright"),
            "register_link" : event.get("register_link"),
            "location" : event.get("location"),
            "info" : event.get("info"),
            "created_at" : datetime.datetime.now().strftime("%Y-%m-%d"),
            "event_id" : event.get("event_id"),
        }
        #doc_id = hashlib.sha256((event["url"] + ",".join(doc.get("date"))).encode()).hexdigest()
        #doc["id"] = doc_id
        res = es.index(index = "smoothcomp_events", doc_type = 'event', id = doc.get("id"), body = doc)
        logging.info(res)        
    except Exception as e:
        logging.error(str(e))


# crawling events and save to db
def events_to_db():
    events = get_events_calendar()
    for i in events:
        try:
            event = get_event_info(i)
            save_to_db(event)
        except Exception as e:
            logging.error(str(e))

# crawling uaejjf events and save to db
def uaejjf_to_db():
    events = uaejjf_get_calendar()
    events = events + uaejjf_past_events()
    for i in events:
        try:
            event = uaejjf_get_event(i)
            uaejjf_save(event)
        except Exception as e:
            logging.error(str(e))

# crawling smoothcomp events and save to db
def smoothcomp_to_db():
    events = smoothcomp_events("upcoming")
    events = events + smoothcomp_events("past")
    for i in events:
        try:
            event = smoothcomp_get_event(i)
            smoothcomp_save(event)
        except Exception as e:
            logging.error(str(e))

# get events from db
def get_events(size, offset):
    query = {
        "match_all" : {}
    }
    sort = [
        {
          "date": {
            "order": "asc"
          }
        }
      ]
    res = es.search(index = 'bjj_test', body = {'query' : query, 'size' : size, 'from' : offset, 'sort' : sort})
    fin = []
    for item in res['hits']['hits']:
        current = {
            "url" : item['_source']['url'],
            "date" : item['_source']['date'],
            "name" : item['_source']['name'],
            "location" : item['_source']['location'],
            "img" : item['_source']['img'],
            "ranking" : item['_source']['ranking'],
            }
        fin.append(current)
    return fin

# get upcoming events from db (5 days)
def get_upcoming_events():
    #now = datetime.datetime.now()
    #end_date = now + datetime.timedelta(days=7)
    query = {
        "range" : {
            "date" : {
                #"gte" : now.strftime("%Y-%m-%d"),
                #"lte" : end_date.strftime("%Y-%m-%d"),
                "gte" : "now",
                "lte" :  "now+2w",
                "boost" : 2.0
        }
      }
    }
    sort = [
        {
          "date": {
            "order": "asc"
          }
        }
      ]
    res = es.search(index = 'bjj_test', body = {'query' : query, 'size' : 5, 'sort' : sort})
    fin = []
    for item in res['hits']['hits']:
        current = {
            "url" : item['_source']['url'],
            "date" : item['_source']['date'],
            "name" : item['_source']['name'],
            "location" : item['_source']['location'],
            "img" : item['_source']['img'],
            "ranking" : item['_source']['ranking'],
            }
        fin.append(current)
    return fin

# get upcoming events from db uaejjf (1 month)
def uaejjf_get_upcoming_events():
    #now = datetime.datetime.now()
    #end_date = now + datetime.timedelta(days=7)
    query = {
        "range" : {
            "date" : {
                #"gte" : now.strftime("%Y-%m-%d"),
                #"lte" : end_date.strftime("%Y-%m-%d"),
                "gte" : "now",
                "lte" :  "now+1M",
                "boost" : 2.0
        }
      }
    }
    sort = [
        {
          "date": {
            "order": "asc"
          }
        }
      ]
    res = es.search(index = 'uaejjf_test', body = {'query' : query, 'size' : 5, 'sort' : sort})
    fin = []
    for item in res['hits']['hits']:
        current = {
            "url" : item['_source']['url'],
            "date" : item['_source']['date'],
            "name" : item['_source']['name'],
            "location" : item['_source']['location'],
            "img" : item['_source']['img'],
            "register" : item['_source']['register_link'],
            }
        fin.append(current)
    return fin

# get upcoming events from db smoothcomp
def smoothcomp_get_upcoming_events():
    query = {
        "range" : {
            "date" : {
                "gte" : "now",
                "lte" :  "now+1w",
                "boost" : 2.0
        }
      }
    }
    sort = [
        {
          "date": {
            "order": "asc"
          }
        }
      ]
    res = es.search(index = 'smoothcomp_events', body = {'query' : query, 'size' : 10, 'sort' : sort})
    fin = []
    for item in res['hits']['hits']:
        current = {
            "url" : item['_source']['url'],
            "date" : item['_source']['date'],
            "name" : item['_source']['name'],
            "location" : item['_source']['location'],
            "img" : item['_source']['img'],
            "register" : item['_source']['register_link'],
            }
        fin.append(current)
    return fin


# get all upcoming events
def get_upcoming_all():
    #now = datetime.datetime.now()
    #end_date = now + datetime.timedelta(days=7)
    query = {
        "range" : {
            "date" : {
                "gte" : "now",
                "lte" :  "now+1M",
                "boost" : 2.0
        }
      }
    }
    sort = [
        {
          "date": {
            "order": "asc"
          }
        }
      ]
    res = es.search(index = 'smoothcomp_events,uaejjf_test', body = {'query' : query, 'size' : 25, 'sort' : sort})
    fin = []
    for item in res['hits']['hits']:
        current = {
            "url" : item['_source']['url'],
            "date" : item['_source']['date'],
            "name" : item['_source']['name'],
            "location" : item['_source']['location'],
            "img" : item['_source']['img'],
            #"register" : item['_source']['register_link'],
            }
        fin.append(current)
    return fin

# get event by id
def get_event_by_id(event_id):
    res = es.get(index = "bjj_test", doc_type = 'event', id = event_id)
    item = res["_source"]
    current = {
        "url" : item['url'],
        "date" : item['date'],
        "name" : item['name'],
        #"img" : item['img'],
        "info" : item["info"],
        "ranking" : item['ranking'],
    }
    return current

# get event by id uaejjf
def uaejjf_event_by_id(event_id):
    try:
        res = es.get(index = 'uaejjf_test', doc_type = 'event', id = event_id)
        item =  res['_source']
        current = {
            "url" : item['url'],
            "name" : item['name'],
            "event_id" : item['event_id'],
            "date" : item['date'],
            }
        return current
    except Exception as e:
        logging.error(str(e))
    return {}

# get event by id smoothcomp
def smoothcomp_event_by_id(event_id):
    try:
        res = es.get(index = 'smoothcomp_events', doc_type = 'event', id = event_id)
        item =  res['_source']
        current = {
            "url" : item['url'],
            "name" : item['name'],
            "event_id" : item['event_id'],
            "date" : item['date'],
            }
        return current
    except Exception as e:
        logging.error(str(e))
    return {}

# get last uaejjf events
def uaejjf_last_events():
    query = {
        "range" : {
            "date" : {
                #"gte" : now.strftime("%Y-%m-%d"),
                #"lte" : end_date.strftime("%Y-%m-%d"),
                "gte" : "now-3M",
                "lte" :  "now",
                "boost" : 2.0
        }
      }
    }
    sort = [
        {
          "date": {
            "order": "desc"
          }
        }
      ]
    res = es.search(index = 'uaejjf_test', body = {'query' : query, 'size' : 25, 'sort' : sort})
    fin = []
    for item in res['hits']['hits']:
        current = {
            "url" : item['_source']['url'],
            "date" : item['_source']['date'],
            "name" : item['_source']['name'],
            "event_id" : item['_source']['event_id'],
            }
        fin.append(current)
    return fin

# get last smoothcomp events
def smoothcomp_last_events():
    query = {
        "range" : {
            "date" : {
                #"gte" : now.strftime("%Y-%m-%d"),
                #"lte" : end_date.strftime("%Y-%m-%d"),
                "gte" : "now-2M",
                "lte" :  "now",
                "boost" : 2.0
        }
      }
    }
    sort = [
        {
          "date": {
            "order": "desc"
          }
        }
      ]
    res = es.search(index = 'smoothcomp_events', body = {'query' : query, 'size' : 25, 'sort' : sort})
    fin = []
    for item in res['hits']['hits']:
        current = {
            "url" : item['_source']['url'],
            "date" : item['_source']['date'],
            "name" : item['_source']['name'],
            "event_id" : item['_source']['event_id'],
            }
        fin.append(current)
    return fin


# get uaejjf event result KZ
def uaejjf_event_result(event_id = None, source = 'uaejjf'):
    if source == 'uaejjf':
        link = "https://ajptour.com/en/event/{}/results".format(event_id)
    else:
        link = "https://smoothcomp.com/en/event/{}/results".format(event_id)

    s = requests.session()
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0'
    }
    r = s.get(url = link, headers = headers)
    if r.ok:
        event = r.text
        tree = lxml.html.fromstring(event)
        token = tree.xpath(".//meta[contains(@name,'csrf')]/@content")
        event_name = tree.xpath(".//title")
        event_name = event_name[0].text_content().strip("\n").strip()
        token = token[0]
        data = {
            'competitorname' : '',
            'groupname' : '',
            'academy' : '',
            'team' : '',
            'country' : 'KZ',
            '_token' : token,
        }
        cookies = s.cookies.get_dict()
        cookies = ';'.join("{!s}={!s}".format(key,val) for (key,val) in cookies.items())

        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
            'content-type' : 'application/x-www-form-urlencoded',
            'cookie' : cookies,
        }
        r = s.post(url = link, data = data, headers = headers)
        if r.ok:
            result = r.text
            tree = lxml.html.fromstring(result)

            gold_medals = tree.xpath(".//div[contains(@class, 'total-medals')]//div[contains(@class, '-gold')]//strong")
            gold_medals = gold_medals[0].text_content().strip() if gold_medals else "0"

            silver_medals = tree.xpath(".//div[contains(@class, 'total-medals')]//div[contains(@class, '-silver')]//strong")
            silver_medals = silver_medals[0].text_content().strip() if silver_medals else "0"
            
            bronze_medals = tree.xpath(".//div[contains(@class, 'total-medals')]//div[contains(@class, '-bronze')]//strong")
            bronze_medals = bronze_medals[0].text_content().strip() if bronze_medals else "0"

            results = tree.xpath(".//div[contains(@id, 'results')]//div[contains(@class, 'result')]")
            all_athletes = []
            for item in results:

                division = item.xpath(".//h2")
                div = division[0].text_content().strip("\n") if division else ''

                athletes = item.xpath(".//div[contains(@class, 'well-inverted')]//div[contains(@class, 'row')]")
                for a in athletes:            
                    current = {}
                    current['division'] = div

                    place = a.xpath(".//div[contains(@class, 'place ')]")
                    current['place'] = place[0].text_content().strip("\n") if place else ''

                    name = a.xpath(".//h3[contains(@class, 'name')]")
                    current['name'] = name[0].text_content().strip("\n").replace("\n\n\n", " ") if name else ''

                    profile_link = a.xpath(".//h3[contains(@class, 'name')]//a/@href")
                    current['profile_id'] = profile_link[0].strip("/").split("/")[-1] if profile_link else ''

                    team = a.xpath(".//span[contains(@class, 'club')]")
                    current['team'] = team[0].text_content().strip("\n") if team else ''

                    all_athletes.append(current)

            all_athletes = list(filter(lambda a: "Kazakhstan" in a['name'], all_athletes))
            
            info = {
                "event" : event_name, 
                "athletes" : all_athletes,
                "gold" : gold_medals,
                "silver" : silver_medals,
                "bronze" : bronze_medals,
                }
            return info
    return None

# get uaejjf profile info
def uaejjf_parse_profile(profile_id):
    profile_id = re.sub("[^0-9]", "", profile_id)
    if profile_id:
        link = "https://ajptour.com/en/profile/{}".format(profile_id)
        s = requests.session()
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0'
        }
        r = s.get(url = link, headers = headers)
        if r.ok:
            profile = r.text
            
            tree = lxml.html.fromstring(profile)
            profile = {
                "id" : profile_id,
                "url" : link,
            }

            name = tree.xpath(".//div[contains(@class, 'user-info')]//h1")    
            profile['name'] = name[0].text_content().strip() if name else ''

            img = tree.xpath(".//img[contains(@class, 'image-user')]/@src")
            profile['img'] = img[0] if img else ''

            img_default = tree.xpath(".//img[contains(@class, 'Federation logo')]/@src")
            if not profile.get("img"):
                profile['img'] = img_default[0]

            details = tree.xpath(".//div[@class='user-details']//span[contains(@class, 'margin-horizontal-xs-16')]")
            user_info = {}

            total_gold = 0
            total_silver = 0
            total_bronze = 0

            for d in details:
                key = d.xpath(".//small[contains(@class, 'mute')]")
                key = key[0].text_content().strip().lower() if key else ''

                val = d.xpath(".//span[contains(@class, 'details-data')]")
                val = val[0].text_content().strip() if val else ''

                user_info[key] = val

            profile['info'] = user_info

            event_matches = tree.xpath(".//div[contains(@class, 'event')]//div[contains(@class, 'panel-matches')]")
            events = []

            for event in event_matches:   
                matches = []

                event_id = event.xpath(".//div[contains(@class, 'panel-heading')]//a/@href")
                event_id = event_id[0].split("/bracket/")[0].strip().split("/")[-1] if event_id else None

                bracket_id = event.xpath(".//div[contains(@class, 'panel-heading')]//a/@href")
                bracket_id = bracket_id[0].strip().split("/")[-1] if bracket_id else None

                division = event.xpath(".//h2[contains(@class, 'panel-title')]//span")
                division = division[0].text_content() if division else ''

                place = event.xpath(".//div[contains(@class, 'row')][last()]//div[contains(@class, 'md-7')]")
                place = place[0].text_content().strip().replace("Placement ", "") if place else ''

                if place:
                    if place == '1':
                        total_gold += 1
                    elif place == '2':
                        total_silver += 1
                    elif place == '3':
                        total_bronze += 1

                matches_list = event.xpath(".//div[contains(@class, 'matches-list')]//div[contains(@class, 'row')]")

                current_event = {
                    "event" : uaejjf_event_by_id(event_id), # if resource == "uaejjf" else smoothcomp_event_by_id(event_id),
                    "place" : place,
                }

                for m in matches_list:
                    result = m.xpath(".//div[contains(@class, 'md-2')]")
                    result = result[0].text_content().strip() if result else ''

                    competitor = m.xpath(".//div[contains(@class, 'md-6')]")
                    competitor = competitor[0].text_content().strip() if competitor else ''

                    match_info = m.xpath(".//div[contains(@class, 'md-4 muted')]")
                    match_info = match_info[0].text_content().strip() if match_info else ''
                
                    match = {
                        "division" : division, 
                        "result" : result, 
                        "competitor" : competitor,
                        "info" : match_info,
                        "bracket" : bracket_id,
                    }
                    matches.append(match)

                current_event["matches"] = matches
                events.append(current_event)

            profile['event_matches'] = events
            profile['medals'] = {"gold" : total_gold, "silver" : total_silver, "bronze" : total_bronze}

            return profile
    return {}

def smoothcomp_parse_profile(profile_id):
    profile_id = re.sub("[^0-9]", "", profile_id)
    if profile_id:
        link = "https://smoothcomp.com/en/profile/{}".format(profile_id)
        s = requests.session()
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0'
        }
        r = s.get(url = link, headers = headers)
        if r.ok:
            profile = r.text
            
            tree = lxml.html.fromstring(profile)
            profile = {
                "id" : profile_id,
                "url" : link,
            }

            name = tree.xpath(".//div[contains(@class, 'user-info')]//h1")    
            profile['name'] = name[0].text_content().strip() if name else ''

            img = tree.xpath(".//img[contains(@class, 'image-user')]/@src")
            profile['img'] = img[0] if img else ''

            #if not profile.get("img"):
            #    profile['img'] = "http://10.10.1.143:58095/static/img/user.png"

            details = tree.xpath(".//div[@class='user-details']//span[contains(@class, 'margin-horizontal-xs-16')]")

            total_gold = 0
            total_silver = 0
            total_bronze = 0

            user_info = {}

            for d in details:
                key = d.xpath(".//small[contains(@class, 'mute')]")
                key = key[0].text_content().strip().lower() if key else ''

                val = d.xpath(".//span[contains(@class, 'details-data')]")
                val = val[0].text_content().strip() if val else ''

                user_info[key] = val

            profile['info'] = user_info

            event_matches = tree.xpath(".//div[contains(@class, 'event')]//div[contains(@class, 'panel-matches')]")
            events = []

            for event in event_matches:   
                matches = []

                event_id = event.xpath(".//div[contains(@class, 'panel-heading')]//a/@href")
                event_id = event_id[0].split("/bracket/")[0].strip().split("/")[-1] if event_id else None

                bracket_id = event.xpath(".//div[contains(@class, 'panel-heading')]//a/@href")
                bracket_id = bracket_id[0].strip().split("/")[-1] if bracket_id else None

                division = event.xpath(".//h2[contains(@class, 'panel-title')]//span")
                division = division[0].text_content() if division else ''

                place = event.xpath(".//div[contains(@class, 'row')][last()]//div[contains(@class, 'md-7')]")
                place = place[0].text_content().strip().replace("Placement ", "") if place else ''

                if place:
                    if place == '1':
                        total_gold += 1
                    elif place == '2':
                        total_silver += 1
                    elif place == '3':
                        total_bronze += 1                    

                matches_list = event.xpath(".//div[contains(@class, 'matches-list')]//div[contains(@class, 'row flex-')]")

                current_event = {
                    "event" : smoothcomp_event_by_id(event_id),
                    "place" : place,
                }

                for m in matches_list:
                    result = m.xpath(".//div[contains(@class, 'md-2')]")
                    result = result[0].text_content().strip() if result else ''

                    competitor = m.xpath(".//div[contains(@class, 'md-4')]")
                    competitor = competitor[0].text_content().strip() if competitor else ''

                    match_info = m.xpath(".//div[contains(@class, 'md-4 muted')]")
                    match_info = match_info[0].text_content().strip() if match_info else ''
                
                    match = {
                        "division" : division, 
                        "result" : result, 
                        "competitor" : competitor,
                        "info" : match_info,
                        "bracket" : bracket_id,
                    }
                    matches.append(match)

                current_event["matches"] = matches
                events.append(current_event)

            profile['event_matches'] = events
            profile['medals'] = {"gold" : total_gold, "silver" : total_silver, "bronze" : total_bronze}

            return profile
    return {}

# uaejjf save profile
def uaejjf_save_profile(profile):
    try:
        if profile:
            if profile.get("img"):
                if not profile.get("img").startswith("https://ajptour.com"):
                    profile['img'] = "https://ajptour.com" + profile.get("img")
                if profile.get("img").startswith("//ajptour"):
                    profile['img'] = "https:" + profile.get("img")
        
                # save image
                r = requests.get(profile.get("img"))
                if r.ok:
                    img = str(base64.b64encode(r.content).decode("utf-8"))
            else:
                r = requests.get("http://10.10.1.143:58095/static/img/user.png")
                if r.ok:
                    img = str(base64.b64encode(r.content).decode("utf-8"))

            profile['img'] = img
            profile['created_at'] = datetime.datetime.now().strftime("%Y-%m-%d")
            
            res = es.index(index = "uaejjf_user", doc_type = 'profile', id = profile.get("id"), body = profile)
            logging.info(res)        
    except Exception as e:
        logging.error(str(e))

# smoothcomp save profile
def smoothcomp_save_profile(profile):
    try:
        if profile:
            if profile.get("img"):
                if not profile.get("img").startswith("https://smoothcomp.com"):
                    profile['img'] = "https://smoothcomp.com" + profile.get("img")
                if profile.get("img").startswith("//smoothcomp.com"):
                    profile['img'] = "https:" + profile.get("img")
        
                # save image
                r = requests.get(profile.get("img"))
                if r.ok:
                    img = str(base64.b64encode(r.content).decode("utf-8"))
            else:
                r = requests.get("http://10.10.1.143:58095/static/img/user.png")
                if r.ok:
                    img = str(base64.b64encode(r.content).decode("utf-8"))

            profile['img'] = img
            profile['created_at'] = datetime.datetime.now().strftime("%Y-%m-%d")
            
            res = es.index(index = "smoothcomp_user", doc_type = 'profile', id = profile.get("id"), body = profile)
            logging.info(res)
    except Exception as e:
        logging.error(str(e)) 

# uaejjf save event results
def uaejjf_save_results(event_id):
    try:
        results = uaejjf_event_result(event_id = event_id)
        results['created_at'] = datetime.datetime.now().strftime("%Y-%m-%d")

        if results.get("athletes"):
            for i in results.get("athletes"):
                profile = uaejjf_parse_profile(i.get("profile_id"))
                uaejjf_save_profile(profile)

        res = es.index(index = "uaejjf_results", doc_type = 'athletes_result', id = event_id, body = results)
        logging.info(res)        
    except Exception as e:
       logging.error(str(e))

# smoothcomp save event results
def smoothcomp_save_results(event_id):
    try:
        results = uaejjf_event_result(event_id = event_id, source = 'smoothcomp')
        results['created_at'] = datetime.datetime.now().strftime("%Y-%m-%d")

        if results.get("athletes"):
            for i in results.get("athletes"):
                profile = smoothcomp_parse_profile(i.get("profile_id"))
                smoothcomp_save_profile(profile)
        
        res = es.index(index = "smoothcomp_results", doc_type = 'athletes_result', id = event_id, body = results)
        logging.info(res)
    except Exception as e:
        logging.error(str(e))


# get uaejjf profile from db
def uaejjf_get_profile(profile_id):
    res = es.get(index = 'uaejjf_user', doc_type = 'profile', id = profile_id)
    return res["_source"] if res else None

# get smoothcomp profile from db
def smoothcomp_get_profile(profile_id):
    res = es.get(index = 'smoothcomp_user', doc_type = 'profile', id = profile_id)
    return res["_source"] if res else None

# get uaejjf event result from db
def uaejjf_get_results(event_id):
    res = es.get(index = 'uaejjf_results', doc_type = 'athletes_result', id = event_id)
    return res["_source"] if res else None

# get smoothcomp event result from db
def smoothcomp_get_results(event_id):
    res = es.get(index = 'smoothcomp_results', doc_type = 'athletes_result', id = event_id)
    return res["_source"] if res else None

# get uaejjf events with KZ results
def uaejjf_get_events_kz():
    query = {
        "exists" : { "field" : "athletes" }
    }
    sort = [
        {
          "created_at": {
            "order": "desc"
          }
        }
      ]
    res = es.search(index = 'uaejjf_results', body = {'query' : query, 'size' : 25, 'from' : 0, 'sort' : sort})
    fin = []
    for item in res['hits']['hits']:
        current = uaejjf_event_by_id(item["_id"])
        fin.append(current)
    return fin
        

# save profiles
def uaejjf_save_profiles_kz():
    query = {
        "exists" : { "field" : "athletes" }
    }
    sort = [
        {
          "created_at": {
            "order": "desc"
          }
        }
      ]
    profiles = set()
    res = es.search(index = 'uaejjf_results', body = {'query' : query, 'size' : 50, 'from' : 0, 'sort' : sort})
    for item in res['hits']['hits']:
        athletes = item["_source"]["athletes"]
        for a in athletes:
            profiles.add(a.get("profile_id"))
    
    profiles = list(filter(None, list(profiles)))
    for i in profiles:
        profile = uaejjf_parse_profile(i)
        uaejjf_save_profile(profile)
