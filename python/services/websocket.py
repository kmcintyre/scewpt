from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory

from amazon.dynamo import Connection, Tweet, User

from app import keys, fixed, communication_keys, time_keys
from twitter import twitter_keys


import json
import time
import pickle
import Cookie

from twisted.internet import reactor, defer, threads

shell_data = {
    communication_keys.websocket_ts_start: int(time.time()),
    communication_keys.websocket_tx_filtered: 0,
    communication_keys.websocket_tx: 0,
    communication_keys.websocket_rx: 0
}

def clean_website(website):
    if website.startswith('http://'):
        website = website[7:]
    try:
        return '.'.join(website.split(':')[0].split('.')[-2:])
    except:
        return website.split(':')[0]
                
def get_cookies(request):
    try:
        cookie = Cookie.SimpleCookie().load(request)
        print 'cookie:', cookie
        return cookie
    except Exception as e:
        print 'no cookies:', e
        return []

site_leagues = {}
def unblocked(site, blocked):    
    if site not in site_leagues:
        site_leagues[site] = User().get_league_names(site) 
    return [l for l in site_leagues[site] if l not in blocked]
    
class EmptyResults(Exception):
    
    pass

class TwitterServerProtocol(WebSocketServerProtocol):

    stream_delay = 1

    def onConnect(self, request):
        print 'connect:', request
        try:
            self.user = Connection().new_client({
                communication_keys.websocket_key: request.headers['sec-websocket-key'],
                communication_keys.websocket_ip: request.peer.split(':')[1],
                communication_keys.websocket_ts_start: int(time.time()),
                communication_keys.websocket_tx_filtered: 0,
                communication_keys.websocket_tx: 0,
                communication_keys.websocket_rx: 0
            })
            if request.origin:
                website = clean_website(communication_keys.host(request.origin))
                print 'origin website:', website
                self.user[communication_keys.client_website] = [website]
            elif 'host' in request.headers:
                website = clean_website(request.headers['host'])
                print 'host website:', website                
                self.user[communication_keys.client_website] = [website]
            if 'cookie' in request.headers:
                print 'cookies:', request.headers
                self.user[communication_keys.websocket_cookies] = get_cookies(
                    request.headers['cookie'].encode('utf8', errors='ignore'))
            else:
                print 'no client cookies'
            if hasattr(self.factory, 'server_details'):
                self.user[communication_keys.websocket_server] = self.factory.server_details
        except Exception as e:
            print 'on connect exception:', e

    def onOpen(self):
        print 'open:', self.peer
        self.factory.associate(self)
        try:
            print 'connected user:', self.user._data
        except Exception as e:
            print 'connection exception:', e

    def jsonPulse(self, update = None):        
        pulse = {}
        pulse.update(self.user._data)
        self.user[communication_keys.websocket_tx] += 1
        if update:            
            pulse.update(update)
        self.sendMessage(json.dumps(pulse))
        
    def onJsonMessageClient(self, incoming):        
        print 'incoming client message:', incoming
        if communication_keys.client_location in incoming and communication_keys.client_location not in self.user:
            print 'set location:', incoming[communication_keys.client_location]
            self.user[communication_keys.client_location] = incoming[communication_keys.client_location]
            if self.user[communication_keys.client_location][communication_keys.client_location_latitude]:
                try:
                    self.user[communication_keys.client_location][communication_keys.client_location_latitude] = str(self.user[communication_keys.client_location][communication_keys.client_location_latitude])
                except Exception as e:
                    print 'exception storing latitude:', e
            if self.user[communication_keys.client_location][communication_keys.client_location_longitude]:
                try:
                    self.user[communication_keys.client_location][communication_keys.client_location_longitude] = str(
                        self.user[communication_keys.client_location][communication_keys.client_location_longitude])
                except Exception as e:
                    print 'exception storing longitude:', e
        if communication_keys.client_start in incoming and communication_keys.client_start not in self.user:
            self.user[communication_keys.client_start] = incoming[communication_keys.client_start]
            for ll in [c for c in self.factory.clients if keys.entity_latlong in c.user]:
                print 'long lat:'                
                ll.sendMessage(json.dumps(self.user._data))
        if communication_keys.client_first_here in incoming and communication_keys.client_first_here not in self.user:
            self.user[communication_keys.client_first_here] = incoming[
                communication_keys.client_first_here]
        
    def onJsonMessage(self, incoming):
        #print 'json message:', incoming
        if Tweet.tweet_id in incoming: 
            tsent = self.factory.disperse_social(incoming)
            print 'total sent:', tsent                        
        elif Connection.webrole in incoming:
            webrole = incoming[Connection.webrole]
            print 'update webrole:', webrole
            self.user._data.update(incoming[Connection.webrole])
        elif communication_keys.client_website in incoming:
            if communication_keys.client_website not in self.user or (incoming[communication_keys.client_website] != self.user[communication_keys.client_website]):                
                print 'set website to list:', incoming[communication_keys.client_website]
                self.user[communication_keys.client_website] = incoming[communication_keys.client_website]
            else:
                print 'update website?:', incoming
        elif communication_keys.client_block in incoming:
            if incoming[communication_keys.client_block]:
                print 'block leagues:', incoming[communication_keys.client_block]
                self.user[communication_keys.client_block] = incoming[communication_keys.client_block]                
            else:
                del self.user[communication_keys.client_website]        
        elif 'backfill' in incoming:
            self.user[communication_keys.websocket_rx] += 1
            print 'backfill:', incoming['backfill']
            if incoming['backfill']:
                self.factory.backfill_twitter(self, incoming)
            else:
                print 'ignored!', incoming

    def onNonBinaryMessage(self, payload):        
        print 'non binary:', payload.__class__.__name__, len(payload) 

    def onMessage(self, payload, isBinary):
        try:
            self.user[communication_keys.websocket_rx] += 1                        
        except Exception as e:            
            print 'rx exception:', e
        if not isBinary:
            try: 
                j = json.loads(payload.decode('utf8'))
                self.onJsonMessage(j)
            except AttributeError as e:
                print 'attribute error:', e
            except ValueError as e:
                print 'value error:', e
            except KeyError as e:
                print 'key error:', e
                self.onNonBinaryMessage(payload.decode('utf8'))                
            except Exception as e:
                print 'ut-oh:', e, e.__class__.__name__, payload
                self.onNonBinaryMessage(payload.decode('utf8'))
        elif isBinary and communication_keys.channel in self.user:
            self.user[communication_keys.websocket_rx] += 1
            self.factory.disperse_instagram(payload)
        else:
            print 'something else?:'

    def onClose(self, wasClean, code, reason):
        try:
            self.user[communication_keys.websocket_ts_end] = int(time.time())            
            self.user.save()            
            print 'connection close', fixed.lingo_since(self.user, communication_keys.websocket_ts_start ), self.user._data
        except Exception as e:
            print 'disassociate exception:', e
        try:
            print self.user._data
        except:
            pass
        self.factory.disassociate(self)

class TwitterServerFactory(WebSocketServerFactory):

    protocol = TwitterServerProtocol
    heartbeat_int = 60

    def __init__(self, url, debug=False):
        WebSocketServerFactory.__init__(
            self, url)
        self.clients = []
        self.program_queue = defer.DeferredQueue()
        self.prime_queue()
        print 'init heartbeat_int:', self.heartbeat_int
        reactor.callLater(self.heartbeat_int, self.heartbeat)

    def prime_queue(self, ign=None):
        d = self.program_queue.get()
        d.addBoth(self.serve_program)
        d.addBoth(self.prime_queue)

    def serve_program(self, client_league_seq):
        try:
            print 'serve_program:', client_league_seq[1]
            program = self.ws_program(client_league_seq[1])
            client_league_seq[0].sendMessage(pickle.dumps(program), True)
        except:
            try:
                print 'serve_program error:', client_league_seq[1]
                client_league_seq[0].transport.loseConnection()
            except:
                pass

    def json_from_tweet(self, tweet):
        return json.loads(tweet[5:int(tweet[:5].strip()) + 5])


    def check_filter_rule(self, k, v, msg):
        if isinstance(v, bool):
            if v == bool(k in msg):
                return True
        else:
            print 'check:', k, ' in ', v, ' value: ', msg[k]
            try:
                if msg[k] in v or v in msg[k]:
                    return True
            except Exception as e:
                print 'filter check error:', e
        return False
        
    def cheap_filter(self, msg, fi):
        for k, v in fi.iteritems():
            if not self.check_filter_rule(k, v, msg):
                return True
        return False

    def filter_social(self, client, social_json):
        if client.user[communication_keys.channel]:
            if client.user[communication_keys.channel_filter]:
                if not self.cheap_filter(social_json, client.user[communication_keys.channel_filter]):
                    print 'send to:', client.user[communication_keys.channel], client.user[communication_keys.channel_filter]
                    client.user[communication_keys.websocket_tx] += 1
                    return False
                else:
                    print 'filtered to:', client.user[communication_keys.channel_filter]
            else:
                pass
                #print 'no filter:', client.user._data
        elif client.user[communication_keys.client_website] and social_json[keys.entity_site] in client.user[communication_keys.client_website] and (not client.user[communication_keys.client_block] or social_json[keys.entity_league] not in unblocked(client.user[communication_keys.client_website][0], client.user[communication_keys.client_block])):
            client.user[communication_keys.websocket_tx] += 1
            return False
        else:
            print 'filter user:', client.user._data
        client.user[communication_keys.websocket_tx_filtered] += 1
        return True
                
    def recognized_mentions(self, tweet):
        if twitter_keys.entities in tweet and twitter_keys.user_mentions in tweet[twitter_keys.entities]:
            leagues_mentioned = set([])
            for mention in tweet[twitter_keys.entities][twitter_keys.user_mentions]:
                if keys.entity_league in mention:
                    for league in mention[keys.entity_league]:
                        leagues_mentioned.add(league)
            print 'leagues_mentioned:', leagues_mentioned
            '''
            if keys.tweet_recognized_mentions in social_json and c.user[keys.operator] in leagues_mentioned:
                print 'sent to:', c.user[keys.operator], 'from:', social_json[keys.entity_league], social_json[keys.entity_twitter], 'for:', [k for k in social_json[keys.tweet_recognized_mentions].keys() if c.user[keys.operator] in social_json[keys.tweet_recognized_mentions][k]]
                if c.user[keys.operator] != social_json[keys.entity_league]:
                    c.sendMessage(json.dumps(social_json))
                    total_sent += 1                    
            '''
    def disperse_social(self, social_json, msg_binary=None):
        print 'disperse_social:', social_json[keys.entity_site], social_json[keys.entity_league], social_json[Tweet.tweet_user_id], social_json[Tweet.tweet_id]
        total_sent = 0 
        for c in self.clients:    
            if communication_keys.client_website in c.user:
                if not self.filter_social(c, social_json): 
                    print 'send to user:', c.user[communication_keys.websocket_ip], social_json[keys.entity_league], c.user[communication_keys.websocket_tx]
                    if not msg_binary:
                        c.sendMessage(json.dumps(social_json))
                    else:
                        c.sendMessage(msg_binary, True)
                    total_sent += 1                    
            else:
                print 'unknown user:', c.user._data
        return total_sent
    
    def disperse_instagram(self, instagram):
        print 'disperse instagram:', len(self.clients), 'total clients'
        instagram_json = self.json_from_tweet(instagram)
        self.disperse_social(instagram_json, instagram)
        
    def filling(self, query_result):
        wo = []
        try:
            for t in query_result:
                ff = {}
                ff.update(t._data)
                print 'found-1:', ff[keys.entity_twitter], fixed.lingo_since_date(int(ff[Tweet.ts_ms]) / 1000)            
                wo.append(ff)
            if len(wo) == 0:
                #print 'empty result:', incoming
                raise EmptyResults()                
            print 'wo length:', len(wo)
            return wo
        except Exception as e:
            print 'filling exception:', e

    def fill_kwargs(self, client, limit, last, backfill):
        kwargs = {'limit': limit , 'reverse': backfill }
        #if keys.entity_league not in ff:                
        kwargs['site__eq'] = client.user[communication_keys.client_website][0]
        if last:
            kwargs['_tweet_id__lt'] = last
        kwargs['index'] = Tweet.index_site
        if client.user[communication_keys.client_block]:
            ub = unblocked(client.user[communication_keys.client_website][0], client.user[communication_keys.client_block])
            kwargs['query_filter'] = { 'league__in': ub }
            #pass
            #kwargs['query_filter'] = {'social_act__eq': 'tweet' }
            #if twitter_keys.tweet_id in ff:                
            #    tweet_key = 'social_composite__lt' if backfill else 'social_composite__gt'
            #    kwargs['query_filter'][tweet_key] = 'tweet ' + ff[twitter_keys.tweet_id]             
        #else:
        #    if twitter_keys.tweet_id in ff:
        #        tweet_key = 'social_composite__lt' if backfill else 'social_composite__gt'
        #        kwargs[tweet_key] = 'tweet ' + ff[twitter_keys.tweet_id] 
        return kwargs

    def backfill_twitter(self, client, incoming):
        bf = incoming['backfill']
        last = incoming['last'] if 'last' in incoming else None
        kwargs = self.fill_kwargs(client, bf, last, True)
        print 'backfill args:', kwargs
        
        threads.deferToThread(Tweet().query_2, **kwargs).addCallback(self.filling).addCallback(self.windout, client).addErrback(self.errorout, client, bf)
            
    def errorout(self, err, client, incoming):
        r = err.trap(EmptyResults)
        print 'errorout', r, client.user, incoming
        client.jsonPulse({keys.entity_site: incoming['site'], 'progression': incoming['progression']})        
        #print 'nothing available?', err        

    def windout(self, delivery, client):
        print 'windout-delivery:', len(delivery)
        if delivery:
            try:
                t = delivery[0]
                t['windout'] = len(delivery)
                print 'send windout with remaining:', len(delivery), t[keys.entity_site],  t[keys.entity_league], t[keys.entity_twitter], t[Tweet.tweet_id]
                w = json.dumps(t, cls=fixed.SetEncoder)
                client.sendMessage(w, False)
                if len(t) > 0:
                    reactor.callLater(.5, self.windout, delivery[1:], client)
            except AttributeError as e:
                print 'missing tweet?:', client.user, e.__class__.__name__, e
                self.windout(delivery, client)
            except Exception as e:
                print 'another problem:', client.user, e.__class__.__name__, e

    def associate(self, client):
        print 'associate client:', client.peer
        try:
            self.clients.append(client)
        except Exception as e:
            print 'associate exception:', e

    def disassociate(self, client):
        try:
            self.clients.remove(client)
        except ValueError as e:
            print 'bad client', e
        except Exception as e:
            print 'disassociate exception:', e.__class__.__name__, e

    def heartbeat(self):        
        oc = [c.user._data for c in self.clients if c.user[communication_keys.channel] and c.user[communication_keys.channel] == communication_keys.operator]
        oc_names = [o[keys.entity_league] for o in oc]        
        wc = [c.user._data for c in self.clients if not c.user[communication_keys.channel]]
        if wc:
            print 'web channels:', [o[communication_keys.client_website][0] for o in wc]            
            for c in self.clients:
                hb = { time_keys.ts_heartbeat: int(time.time()), communication_keys.operator_channels: oc_names}
                c.jsonPulse(hb)                
        lc = [c.user._data for c in self.clients if c.user[communication_keys.channel] and c.user[communication_keys.channel] == communication_keys.listener]
        if lc:
            print 'listener channels:', [o[communication_keys.channel_filter] for o in lc]
                     
        reactor.callLater(self.heartbeat_int, self.heartbeat)

factory = TwitterServerFactory("ws://localhost:8080", debug=False)

if __name__ == '__main__':
    reactor.listenTCP(8080, factory)
    reactor.run()
