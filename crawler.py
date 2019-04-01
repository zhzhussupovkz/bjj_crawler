import json
import requests
import lxml.html

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

        img = tree.xpath(".//div[@id='container']//ul[contains(@id,'banner')]//img/@src")
        event_info['img'] = img[0] if img else ""

        name = tree.xpath(".//div[contains(@id, 'post')]//h2")
        event_info['name'] = name[0].text_content() if name else "not found"

        date = tree.xpath(".//div[contains(@id, 'post')]//abbr")
        event_info['date'] = date[0].text_content() if date else "not found"

        location = tree.xpath(".//div[contains(@id, 'post-info')]//address")
        event_info['location'] = location[0].text_content().strip() if location else "not found"

        divisions = tree.xpath(".//div[contains(@id, 'divisions')]//table")
        event_info['divisions'] = divisions[0].text_content() if divisions else "not found"
        return event_info
    return {}
