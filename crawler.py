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

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s: %(levelname)s %(message)s')
es = Elasticsearch(["192.168.0.19:11200", "192.168.0.2:11200", "192.168.0.5:11200"], maxsize=25)

def get_proxy():
    proxy_url = 'https://api.getproxylist.com/proxy?' \
                'apiKey=ffe605ca03ce2bc63433ce44032fed59b13a448b' \
                '&allowsHttps=1' \
                #'&lastTested=600' \
                #'&allowsPost=1' \
                #'&allowsCookies=1' \
                #'&allowsCustomHeaders=1' \
                #'&allowsUserAgentHeader=1' \
                #'&allowsRefererHeader=1' \
                #'&[]anonymity=high'

    r = requests.get(proxy_url)
    if r.ok:
        proxy = json.loads(r.text)
        proxy = str(proxy['ip']) + ':' + str(proxy['port'])
        proxies = {"http": "http://" + proxy, "https": "https://" + proxy}
        return proxies
    return None

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
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    s = requests.session()
    r = s.get(url = "https://events.uaejjf.org/en/federation/1/events", headers = headers)
    if r.ok:
        calendar = r.text
        tree = lxml.html.fromstring(calendar)
        links = tree.xpath(".//section[contains(@id, 'upcoming')]//div[contains(@class, 'event-bg')]//div[contains(@class, 'content')]//a/@href")
        links = list(filter(lambda i: "uaejjf.org" in i, links))
        return links
    return []

# parse current event by link
def get_event_info(link):
    if link.startswith("//ibjjf.com"):
        link = "https:" + link
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    r = requests.get(url = link, headers = headers) #, proxies = get_proxy())
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
def uaejjf_get_event(link):
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

        #name = tree.xpath(".//div[contains(@class, 'cover-heading')]//h1")
        #event_info['name'] = name[0].text_content().strip().replace("\n", "") if name else "not found"

        #name_test = tree.xpath(".//div[contains(@class, 'container')]//h1")
        #event_info['name'] = name_test[0].text_content().strip().replace("\n", "") if name_test else "not found"

        name = tree.xpath(".//title")
        event_info['name'] = name[0].text_content().strip().replace("\n", "") if name else "not found"
        
        date = tree.xpath(".//div[contains(@class, 'date event')]//strong")
        year = datetime.datetime.now().year
        df = ["{} {}".format(i.text_content().replace("\n","").strip(), year) for i in date]
        dates = [dateparser.parse(i) for i in df]
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
        if not event.get("img").startswith("https://events.uaejjf.org"):
            event['img'] = "https://events.uaejjf.org" + event.get("img")
        if event.get("img").startswith("//events"):
            event['img'] = "https:" + event.get("img")
        # save image
        r = requests.get(event.get("img"))
        if r.ok:
            img = str(base64.b64encode(r.content).decode("utf-8"))
        else:
            img = ""
    
        doc = {   
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
        doc_id = hashlib.sha256((event["url"] + ",".join(doc.get("date"))).encode()).hexdigest()
        doc["id"] = doc_id
        res = es.index(index = "uaejjf_test", doc_type = 'event', id = doc.get("id"), body = doc)
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
    for i in events:
        try:
            event = uaejjf_get_event(i)
            uaejjf_save(event)
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
    now = datetime.datetime.now()
    end_date = now + datetime.timedelta(days=7)
    query = {
        "range" : {
            "date" : {
                "gte" : now.strftime("%Y-%m-%d"),
                "lte" : end_date.strftime("%Y-%m-%d"),
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
    res = es.search(index = 'bjj_test', body = {'query' : query, 'size' : 5}) #, 'sort' : sort})
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
def uaejjf_get_upcoming_events():
    now = datetime.datetime.now()
    end_date = now + datetime.timedelta(days=7)
    query = {
        "range" : {
            "date" : {
                "gte" : now.strftime("%Y-%m-%d"),
                "lte" : end_date.strftime("%Y-%m-%d"),
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
    res = es.search(index = 'uaejjf_test', body = {'query' : query, 'size' : 5}) #, 'sort' : sort})
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
    now = datetime.datetime.now()
    end_date = now + datetime.timedelta(days=7)
    query = {
        "range" : {
            "date" : {
                "gte" : now.strftime("%Y-%m-%d"),
                "lte" : end_date.strftime("%Y-%m-%d"),
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
    res = es.search(index = 'bjj_test,uaejjf_test', body = {'query' : query, 'size' : 5}) #, 'sort' : sort})
    fin = []
    for item in res['hits']['hits']:
        current = {
            "url" : item['_source']['url'],
            "date" : item['_source']['date'],
            "name" : item['_source']['name'],
            "location" : item['_source']['location'],
            "img" : item['_source']['img'],
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

# get event by id
def uaejjf_event_by_id(event_id):
    query = {
        "match" : {"event_id" : event_id}
    }
    sort = [
        {
          "date": {
            "order": "asc"
          }
        }
      ]
    res = es.search(index = 'uaejjf_test', body = {'query' : query, 'size' : 1, 'sort' : sort})
    item =  res['hits']['hits'][0]
    current = {
        "url" : item['_source']['url'],
        "name" : item['_source']['name'],
        "event_id" : item['_source']['event_id'],
        }
    return current

# get uaejjf event result KZ
def uaejjf_event_result(event_id):
    link = "https://events.uaejjf.org/en/event/{}/results".format(event_id)
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
        event_name = event_name[0].text_content()
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
            results = tree.xpath(".//div[contains(@id, 'results')]//div[contains(@class, 'result')]")
            all_athletes = []
            for item in results:
                current = {}

                division = item.xpath(".//h2")
                current['division'] = division[0].text_content().strip("\n") if division else ''

                athletes = item.xpath(".//div[contains(@class, 'well-inverted')]")
                for a in athletes:            
                    place = a.xpath(".//div[contains(@class, 'place ')]")
                    current['place'] = place[0].text_content().strip("\n") if place else ''

                    name = a.xpath(".//h3[contains(@class, 'name')]")
                    current['name'] = name[0].text_content().strip("\n").replace("\n\n\n", " ") if name else ''

                    team = a.xpath(".//span[contains(@class, 'club')]")
                    current['team'] = team[0].text_content().strip("\n") if team else ''

                    all_athletes.append(current)
            info = {"event" : event_name, "athletes" : all_athletes}
            return info
    return []

#c = uaejjf_get_calendar()
#uaejjf_get_event(c[-14])
#uaejjf_to_db()

#events_to_db()

#event = uaejjf_get_event("https://events.uaejjf.org/en/event/172")
#uaejjf_save(event)
#print (get_event_by_id("6cd12d98dddba3e141dae9e54f35b4f2366353fcd655dff508d00fa27249f672"))