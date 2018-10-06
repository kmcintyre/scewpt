import json
import datetime
import time
import decimal
import re
import os
import hashlib
from urlparse import urlparse
from bson import json_util

from app import keys, time_keys

tmp_disk = 'ramdisk' if os.path.isdir("/ramdisk") else 'tmp'

from time import mktime

def key_url(k):
    if k.bucket.name == 'socialcss.com': 
        return 'http://socialcss.com.s3-website-us-east-1.amazonaws.com/' + k.key
    else:
        return 'http://s3.amazonaws.com/' + k.bucket.name + '/' + k.key

def key_dt(key):
    from boto.utils import parse_ts
    try:
        modified = time.strptime(key.last_modified, '%a, %d %b %Y %H:%M:%S %Z')
        dt = datetime.datetime.fromtimestamp(mktime(modified))
        return dt
    except:
        return parse_ts(key.last_modified)

def simplify_to_id(inp):
    return ''.join([c for c in inp.lower() if (c.isalnum() and ord(c) < 128) or c == ' ']).strip().replace(' ', "_")

def to_json(obj):
    return json.loads(json_util.dumps(obj))

def simpleurl(url):
    if not urlparse(url).scheme:
        return "http://" + url
    return url

def clean_url(v):
    if v[-1:] == '/':
        return clean_url(v[:-1])
    elif v[:5] == 'https':
        return clean_url('http' + v[5:])
    else:
        return v.strip()

def digest(d):    
    return hashlib.sha224(d).hexdigest()

class SetEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, datetime.datetime):
            return int(time.mktime(obj.timetuple()))
        elif isinstance(obj, decimal.Decimal):
            return int(obj)
        return json.JSONEncoder.default(self, obj)
    
def since(v):
    try:
        return (datetime.datetime.now() - datetime.datetime.fromtimestamp(int(v))).total_seconds()
    except:
        return -1

def days_since(entity, ts_key=time_keys.ts_scout):
    try:
        return (datetime.datetime.now() - datetime.datetime.fromtimestamp(int(entity[ts_key]))).days
    except:
        return -1


def hours_since(entity, ts_key=time_keys.ts_scout):
    try:
        return int((datetime.datetime.now() - datetime.datetime.fromtimestamp(int(entity[ts_key]))).total_seconds() / (60 * 60))
    except:
        return -1


def minutes_since(entity, ts_key=time_keys.ts_scout):
    try:
        return (datetime.datetime.now() - datetime.datetime.fromtimestamp(int(entity[ts_key]))).total_seconds() / 60
    except:
        return -1


def seconds_since(entity, ts_key=time_keys.ts_scout):
    try:
        return (datetime.datetime.now() - datetime.datetime.fromtimestamp(int(entity[ts_key]))).total_seconds()
    except:
        return -1


def lingo_since_date(d):
    return lingo_since({ 'ts': d }, 'ts')

def lingo_since(entity, ts_key=time_keys.ts_scout):
    try:
        dys = days_since(entity, ts_key)
        if dys == 0:
            hrs = hours_since(entity, ts_key)
            if hrs == 0:
                mins = minutes_since(entity, ts_key)
                if mins <= 1:
                    secs = seconds_since(entity, ts_key)
                    if secs == 0:
                        return 'now'
                    return 'secs:', int(secs)
                return 'mins:', int(mins)
            return 'hrs:', int(hrs)
        return 'dys:', int(dys)
    except Exception as e:
        print 'lingo exception:', e
        return -1

def name_flip(name):
    try:
        m = re.search('(.*?), (.*)', name)
        return m.group(2) + ' ' + m.group(1)
    except:
        return name

def adjust_name(entity):
    if keys.entity_name in entity:
        if ',' in entity[keys.entity_name]:
            return name_flip(entity[keys.entity_name]).strip()
        return entity[keys.entity_name].strip()
    elif ':' in entity[keys.entity_profile]:
        n = entity[keys.entity_profile].split(':')[1]
        while n.startswith('/'):
            n = n[1:]
        return n
    else:
        print 'nameless entity:', entity
        
def team_name(entity):
    if keys.entity_team in entity:
        return entity[keys.entity_team]
    elif entity[keys.entity_profile].startswith('team:'):
        return entity[keys.entity_profile][5:]
    else:
        print 'no team:', entity._data
        exit(-1)
        
def check_entity_size(data):
    from twisted.python import reflect
    while len(str(data)) > 2048:
        data = dict(sorted(data.items(), key=lambda seq: len(reflect.safe_str(seq[0])) + len(reflect.safe_str(seq[1])))[:-1])
        return check_entity_size(data)
    return data

def no_drops(entity):
    if keys.entity_no_drops in entity.keys():
        return entity[keys.entity_no_drops]
    else:
        return False

def ordstr(numb):
    if numb < 20:  # determining suffix for < 20
        if numb == 1:
            suffix = 'st'
        elif numb == 2:
            suffix = 'nd'
        elif numb == 3:
            suffix = 'rd'
        else:
            suffix = 'th'
    else:  # determining suffix for > 20
        tens = str(numb)
        tens = tens[-2]
        unit = str(numb)
        unit = unit[-1]
        if tens == "1":
            suffix = "th"
        else:
            if unit == "1":
                suffix = 'st'
            elif unit == "2":
                suffix = 'nd'
            elif unit == "3":
                suffix = 'rd'
            else:
                suffix = 'th'
    return str(numb) + suffix

def filesubpath(filename):
    try:
        os.makedirs(os.path.dirname(filename))
    except:
        pass
    
def qwebchannel():
    uri = os.path.expanduser('~') + '/scewpt/build/qwebchannel.js'
    return open(uri).read()