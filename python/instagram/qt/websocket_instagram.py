import os
os.environ['QTDISPLAY'] = ':2'
from qt import qt5
print 'instagram:', qt5.qt_version

from instagram.qt.browser import InstagramView

import json
import sys

from services.client import SharedClientProtocol
from twisted.internet import reactor, defer

from app import fixed, keys, communication_keys

from services import client

from amazon.dynamo import Tweet, Connection

instagram_queue = defer.DeferredQueue()

ic = InstagramView()
ic.show()    
ic.setFixedWidth(1024)
ic.setFixedHeight(1200)

def prime_queue(ign=None):
    print 'prime_queue:', ign
    instagram_queue.get().addBoth(handle_queue)

def handle_queue(sq):
    print 'handle queue:', ic.page().url().toString()
    url = fixed.simpleurl(sq[0])
    print 'new url:', url
    tweet = Tweet().get_item(_twitter_id=sq[1][Tweet.tweet_user_id],_tweet_id=sq[1][Tweet.tweet_id])
    d = ic.goto_url(url)
    d.addCallback(lambda ign: ic.get_image_data(url, tweet))
    d.addCallback(ic.post_process, tweet)
    d.addBoth(prime_queue)
    return d

prime_queue()

def queue_error(err):
    print 'instagram queue error:', err
        
class InstagramClientProtocol(SharedClientProtocol):
    
    last = None

    def onOpen(self):
        print 'open add filter'
        webrole = {
            communication_keys.channel: communication_keys.listener,
            communication_keys.channel_filter: { Tweet.instagrams: True }
        }
        self.sendMessage(json.dumps({Connection.webrole: webrole }))
    
    def onConnect(self, response):
        super(InstagramClientProtocol, self).onConnect(response)
        print 'Instagram queued!'
        if hasattr(self.factory, 'window'):
            self.factory.window.protocol = self
                    
    def process_instagram(self, incoming, send = False):
        for instagram in incoming[Tweet.instagrams]:
            print 'instagram url:', instagram            
            print 'add to queue instagram:', instagram, instagram_queue.backlog
            instagram_queue.put((instagram, incoming, send))                
    
    def connectionLost(self, reason):
        print 'connectionLost:', reason
        reactor.stop()            
    
    def onMessage(self, payload, isBinary):
        if not isBinary:
            try:
                incoming = json.loads(payload) 
                if Tweet.instagrams in incoming:
                    print 'instagram receipt!', incoming[Tweet.instagrams]
                    print 'site:', incoming[keys.entity_site], 'league:', incoming[keys.entity_league], 'twitter:', incoming[keys.entity_twitter]
                    self.process_instagram(incoming, True)
                else:
                    print 'incoming:', incoming
            except Exception as e:
                print 'message exception:', e
        else:
            print 'message is binary'
            
def init(ep):
    print 'init:', ep
    factory = client.start_client(endpoint, InstagramClientProtocol)
    factory.window = ic 
    
if __name__ == '__main__':
    endpoint = 'localhost'
    if len(sys.argv) > 1:
        endpoint = sys.argv[1]     
    reactor.callWhenRunning(init, endpoint)
    reactor.callLater(60*30, lambda: reactor.stop())
    reactor.run()
