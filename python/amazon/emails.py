import json
from twisted.web.client import getPage
import requests

def get_json_from_msg(msg):
    url = str('http://www.scewpt.com/' + msg + '.json')
    def convert_to_json(response):
        return json.loads(response)
    d = getPage(url)
    d.addCallback(json.loads)
    return d

def get_html_from_msg(msg):
    r = requests.get('http://www.scewpt.com/' + msg + '.html')
    return r.text