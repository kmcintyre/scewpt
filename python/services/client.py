from twisted.internet import reactor, defer, threads

from twisted.internet.protocol import ReconnectingClientFactory
from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol

from twisted.internet.error import ConnectionDone, ConnectionRefusedError

import json
import pickle

import pprint

from pymongo import MongoClient

from app import keys, time_keys, communication_keys
from amazon.dynamo import Tweet, Connection
from pymongo.errors import DuplicateKeyError

def unpayload(payload):
    return threads.deferToThread(pickle.loads, payload)

def hangup(ign, role,  transport):
    if role == 'program':
        print 'hang up on program'
        transport.loseConnection()
    else:
        print 'unknown hangup'
    return defer.SUCCESS


class ReconnectingWebSocketClientFactory(WebSocketClientFactory, ReconnectingClientFactory):

    def startedConnecting(self, connector):
        print 'startedConnecting:', connector.getDestination().host

    def clientConnectionLost(self, connector, reason):
        print 'clientConnectionLost:', connector.getDestination().host, 'reason:', reason
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print 'clientConnectionFailed:', connector.getDestination().host, 'reason:', reason
        ReconnectingClientFactory.clientConnectionFailed(
            self, connector, reason)

class BinaryRepeaterClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        print 'server connect:', response.peer
        self.server = response.peer

    def onOpen(self):
        print 'open:', self.server

    def onMessage(self, payload, isBinary):
        print 'on message:', payload
        if isBinary:
            print 'binary payload:', self.server, len(payload)
            for c in self.factory.clients:
                print 'send to:', c.peer
                reactor.callLater(0, c.sendMessage, payload, isBinary)
        else:
            print 'non-binary skipped'

    def onClose(self, wasClean, code, reason):
        print 'closed wasClean:', wasClean, 'code:', code, 'reason:', reason

class SharedClientProtocol(WebSocketClientProtocol):
    
    def onConnect(self, response):
        print 'client connect:', response
        #print 'sending role on connect:', self.role_msg
        #self.sendMessage(json.dumps(self.role_msg))

    def onClose(self, wasClean, code, reason):
        print 'close:', self.peer, wasClean, code, reason

    def connectionLost(self, reason):
        print 'connectionLost:', reason
        cd = reason.trap(ConnectionDone)
        if cd:
            print 'connection done:', self.factory.__class__.__name__
        else:
            cr = reason.trap(ConnectionRefusedError)
            if cr:
                print 'connection refused:', reason
            else:
                print 'unknown lost:', reason

class ProgramClientProtocol(SharedClientProtocol):

    def report(self, twitter, stats, league, ts):
        print 'called report!:', twitter, stats, league, ts
        self.report_response = defer.Deferred()
        self.sendMessage(json.dumps({'webrole': 'report', 'report': twitter, twitter: stats, keys.entity_league: league, 'ts': ts}))
        return self.report_response

    def onReport(self, payload, isBinary):
        try:
            response = json.loads(payload)
            if 'report_delta' in response:
                print 'difference:', response['report_delta']
                self.report_response.callback(response)
            else:
                print 'received json message:', response
        except ValueError:
            print 'report client assuming init:', payload
        except Exception as e:
            print 'generic error:', e

class WSMailClientProtocol(WebSocketClientProtocol):

    def onOpen(self):
        print 'on open WSMAil'
        try:
            if self.message_filter:
                print 'open: add filter', self.message_filter
                self.sendMessage(json.dumps(self.message_filter))
            else:
                print 'no filter sending all'
        except Exception as e:
            print 'mail exception:', e

    def onMessage(self, payload, isBinary):
        try:
            if self.email_deferred and not self.email_deferred.called:
                self.email_deferred.callback(json.loads(payload))
        except:
            print 'skip message'

def hearing_back(json, email):
    print 'hearing_back:', email
    if json['derived_to'] == email:
        return json
    else:
        raise Exception('hearing back nope:' + json['derived_to'])
    
class ListenerProtocol(WebSocketClientProtocol):
    
    mongo_db = MongoClient().test
    
    sizes = {
        'retweet': 500,
        'conversation': 500,
        'quote': 500,
        'mentions': 500,
        'mentioned': 500
    }

    def onOpen(self):
        print 'open add filter', sorted(self.mongo_db.collection_names())
        for cn in sorted(self.mongo_db.collection_names()):
            count = self.mongo_db[cn].count()
            print cn, 'count:', count 
        webrole = {
            communication_keys.channel: communication_keys.listener,
            communication_keys.channel_filter: { Tweet.tweet_id: True }
        }
        self.sendMessage(json.dumps({Connection.webrole: webrole }))

    def cache(self, tt, sl, msg):
        prefix = tt.split('_', 1)[1]
        #print prefix, sl[0], sl[1], msg[keys.entity_twitter], msg[Tweet.tweet_id]
        for k in sl:
            if prefix == 'conversation' or prefix == 'quote' or prefix == 'retweet':
                ck = prefix + '_' + k
                print 'found:', ck
                if ck not in self.mongo_db.collection_names():
                    print 'missing:', ck, self.sizes[prefix]
                    self.mongo_db.create_collection(ck, capped=True, size=2000 * self.sizes[prefix], max=self.sizes[prefix])
                try:
                    self.mongo_db[ck].insert_one(msg)
                    print 'inserted:', ck
                except DuplicateKeyError:
                    pass
                except Exception as e:
                    print 'conversations/retweet/quote exception:', e
            else:
                mk = prefix + '_' + k
                for mention in msg[Tweet.known_mentions]:
                    
                    try: 
                        if mk not in self.mongo_db.collection_names():
                            print 'missing:', mk, prefix
                            self.mongo_db.create_collection(mk, capped=True, size=2000 * self.sizes[prefix], max=self.sizes[prefix])                    
                        self.mongo_db[mk].insert_one(msg)
                        print 'inserted:', mk
                    except DuplicateKeyError:
                        pass
                    except Exception as e:
                        print 'mentions exception:', e.__class__.__name__
                    
                    if mention[keys.entity_league] != msg[keys.entity_league]:
                        tl = [mention[keys.entity_site].split('.')[0], mention[keys.entity_league]]                        
                        for l in tl:
                            tk = 'mentioned_' + l                            
                            if tk not in self.mongo_db.collection_names():
                                print 'missing:', tk, prefix
                                self.mongo_db.create_collection(tk, capped=True, size=2000 * self.sizes['mentioned'], max=self.sizes['mentioned'])
                                
                            try:
                                self.mongo_db[tk].insert_one(msg)
                                print 'inserted:', tk
                            except DuplicateKeyError:
                                pass                                        
                            except Exception as e:
                                print 'mentioned exception:', e.__class__.__name__
        
    def onMessage(self, payload, isBinary):
        if isBinary:
            print 'ignore binary'
        else:
            try:
                msg = json.loads(payload)
                #print 'msg:', msg
                if Tweet.unknown_retweet in msg:
                    #print 'unknown retweet', msg[keys.entity_league], msg[keys.entity_twitter], msg[Tweet.tweet_id]
                    return                
                try:
                    sl = [msg[keys.entity_site].split('.')[0], msg[keys.entity_league]]
                    #print 'site:', sl[0], 'league:', sl[1]
                    if Tweet.known_retweet in msg:
                        print 'known retweet:', msg[keys.entity_league], msg[keys.entity_twitter], msg[Tweet.known_retweet][keys.entity_league], msg[Tweet.known_retweet][keys.entity_twitter]
                        self.cache(Tweet.known_retweet, sl, msg)
                    if Tweet.known_conversation in msg:
                        print 'known conversation:', msg[keys.entity_league], msg[keys.entity_twitter], msg[Tweet.known_conversation][keys.entity_league], msg[Tweet.known_conversation][keys.entity_twitter]
                        self.cache(Tweet.known_conversation, sl, msg)
                    if Tweet.known_quote in msg:
                        print 'known quote:', msg[keys.entity_league], msg[keys.entity_twitter], msg[Tweet.known_quote][keys.entity_league], msg[Tweet.known_quote][keys.entity_twitter]
                        self.cache(Tweet.known_quote, sl, msg)                                            
                    if Tweet.known_mentions in msg:
                        print 'known mention:', msg[keys.entity_league], msg[keys.entity_twitter]
                        for km in msg[Tweet.known_mentions]:
                            print '    mentioned:', km[keys.entity_league], km[keys.entity_twitter]                        
                        self.cache(Tweet.known_mentions, sl, msg)                        
                except:
                    pass                                        
            except Exception as e:
                print e

def mail_listener(mail_domain='mail.scewpt.com', message_filter_dic=None):
    #client_factory = WebSocketClientFactory('services://' + mail_domain + ':8080', debug=False)
    client_factory = WebSocketClientFactory('ws://mail.scewpt.com:8080')
    print 'mail to unique:', message_filter_dic
    from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
    point = TCP4ClientEndpoint(reactor, mail_domain, 8080)
    report = WSMailClientProtocol()
    report.email_deferred = defer.Deferred()
    report.factory = client_factory
    d = connectProtocol(point, report)
    def msg_filter(protocol=None, mf=None):
        protocol.message_filter = mf        
    d.addCallback(msg_filter, message_filter_dic)
    return report.email_deferred

def start_client(host='localhost', proto=None, port=8080):
    factory = ReconnectingWebSocketClientFactory()
    factory.protocol = proto    
    factory.host = host
    factory.port = port
    print 'client start:', host, port
    reactor.connectTCP(host, port, factory)
    return factory

if __name__ == '__main__':
    class listen():
        start_client('service.athleets.com', ListenerProtocol)
    reactor.callWhenRunning(listen)
    reactor.run()