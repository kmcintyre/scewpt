from amazon.dynamo import Connection, User
from twitter import auth
from app import keys, user_keys, communication_keys
from twitter import twitter_keys
import requests
import json
import sys

import websocket

import threading
import time

import pprint

from twitter.twitter_helper import TwitterLeague

stream_url = 'https://userstream.twitter.com/1.1/user.json'

class StreamLeague(TwitterLeague):
    
    def on_message(self, ws, msg):
        print 'message:', msg

    def on_error(self, ws, msg):
        print 'error:', msg        
                
    def on_open(self, ws):
        self.running = True
        self.welcome()

    def on_close(self, ws):
        self.running = False
        print 'closed!'        
        
    def ws_start(self):
        self.ws.run_forever()
    
    def __init__(self, league_name, endpoint):
        super(StreamLeague, self).__init__(league_name)
        
        self.store = True
        
        self.ws = websocket.WebSocketApp('ws://' + endpoint + ':8080/')
        self.ws.on_message = self.on_message
        self.ws.on_error = self.on_error
        self.ws.on_close = self.on_close
        self.ws.on_open = self.on_open
        
        t2 = threading.Thread(target=self.stream_start)
        t2.daemon = True      
        t2.start()
        
        t = threading.Thread(target=self.ws_start)
        t.daemon = True
        t.start()
        
        while t2.isAlive():
            if t.isAlive():
                time.sleep(1)
            else:
                time.sleep(30)
                t = threading.Thread(target=self.ws_start)
                t.daemon = True
                t.start()
            
        
    def welcome(self):
        print 'send webrole welcome:', self.league
        if self.running:
            self.ws.send(json.dumps({Connection.webrole: { communication_keys.channel: communication_keys.operator, keys.entity_league: self.league }}))
    
    def stream_start(self):
        oauth = auth.get_oauth(self.league_user, self.league_user, self.league_user[user_keys.user_twitter_apps].keys()[0])
        print 'oath:', oauth
        kwargs = { 'url': stream_url, 'auth': oauth, 'stream': True}
        response = requests.post(**kwargs)
        print 'held:', response
        for line in response.iter_lines():
            if line:
                if line == 'Exceeded connection limit for user':
                    time.sleep(120)
                    exit(-1)
                decoded_line = line.decode('utf-8')
                tweet = json.loads(decoded_line)
                try:
                    if twitter_keys.retweeted_status in tweet or twitter_keys.text in tweet:
                        self.process_tweet(tweet)
                    elif 'friends' in tweet:
                        self.process_friends(tweet)
                    elif 'delete' in tweet:
                        self.process_delete(tweet)
                    elif 'event' in tweet:
                        print ' EVENT'
                        pprint.pprint(tweet)
                    elif 'warning' in tweet:
                        print ' WARNING'
                        pprint.pprint(tweet)                        
                    else:
                        pprint.pprint(tweet)
                        exit(-1)                                        
                except Exception as e:
                    print e
                    exit(-1)
   
if __name__ == '__main__':
    endpoint = 'localhost'
    role = sys.argv[1]
    if len(sys.argv) > 2:
        endpoint = sys.argv[2] 
    if not User().get_by_role(role, keys.entity_twitter)[user_keys.user_locked]:
        sl = StreamLeague(role, endpoint)
    else:
        time.sleep(3600)    