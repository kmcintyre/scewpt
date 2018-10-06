from app import time_keys, communication_keys
from amazon.dynamo import User

all_league_names = User().get_league_names()
print all_league_names

from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol
import simplejson as json
import collections

class MissingProtocol(WebSocketClientProtocol):

    def onMessage(self, payload, isBinary):
        if isBinary:
            print 'ignore binary'
        else:
            try:
                msg = json.loads(payload)
                if time_keys.ts_heartbeat in msg:
                    for potential_league in all_league_names:
                        if potential_league not in msg[communication_keys.operator_channels]:
                            print 'missing potential league:', potential_league
                    print 'channel count:', len(msg[communication_keys.operator_channels])
                    if len(msg[communication_keys.operator_channels]) != len(set(msg[communication_keys.operator_channels])):                        
                        duplicates = [item for item, count in collections.Counter(msg[communication_keys.operator_channels]).items() if count > 1]
                        print 'has double!:', duplicates 
            except:
                pass
    
    def onOpen(self):  
        print 'open'

factory = WebSocketClientFactory()
factory.protocol = MissingProtocol
factory.host = 'service.athleets.com'
factory.port = 8080
print 'client start:', factory.host, factory.port
from twisted.internet import reactor

reactor.connectTCP(factory.host, factory.port, factory)
reactor.run()