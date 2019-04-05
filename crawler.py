import json
import requests
import lxml.html
import logging
from elasticsearch import Elasticsearch
import hashlib
import time, datetime
import base64
import random

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

def get_calendar():
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    s = requests.session()
    proxies = get_proxy()
    #if proxies:
    r = s.get(url = "https://ibjjf.com/championships/calendar/", headers = headers) #, proxies = proxies)
    if r.ok:
        calendar = r.text
        tree = lxml.html.fromstring(calendar)
        links = tree.xpath(".//div[contains(@id, 'content')]//table//a/@href")
        return links
    return []

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
        event_info['date'] = date[0].text_content() if date else "not found"

        relevant_dates = tree.xpath(".//div[contains(@id, 'championships-dates')]//ul//li")
        event_info['relevant_dates'] = [i.text_content() for i in relevant_dates] if relevant_dates else []

        location = tree.xpath(".//div[contains(@id, 'post-info')]//address")
        event_info['location'] = location[0].text_content().strip() if location else "not found"

        info = tree.xpath(".//div[contains(@id, 'post-info')]//span")
        event_info['info'] = [i.text_content().strip() for i in info] if info else []

        divisions = tree.xpath(".//div[contains(@id, 'divisions')]//table")
        event_info['divisions'] = divisions[0].text_content() if divisions else "not found"

        return event_info
    return {}

def save_to_db(event):
    try:
        doc_id = hashlib.sha256((event["url"] + str(int(time.time()))).encode()).hexdigest()              
        r = requests.get(event.get("img"))
        if r.ok:
            img = str(base64.b64encode(r.content))
        else:
            img = ""
    
        doc = {   
            "url" : event.get("url"),
            "img" : img,
            "date" : event.get("date"),
            "relevant_dates" : event.get("relevant_dates"),
            "location" : event.get("location"),
            "info" : event.get("info"),
            "created_at" : datetime.datetime.now().strftime("%Y-%m-%d"),
            "other" : {"divisions" : event.get("divisions")},
        }
        doc["id"] = doc_id
        res = es.index(index = "bjj_test", doc_type = 'event', id = doc.get("id"), body = doc)
        logging.info(res)        
    except Exception as e:
        logging.error(str(e))

def events_to_db():
    events = get_calendar()
    for i in events:
        try:
            event = get_event_info(i)
            save_to_db(event)
        except Exception as e:
            logging.error(str(e))
    