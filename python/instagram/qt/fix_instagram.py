import os
os.environ['QTDISPLAY'] = ':2'
from qt import qt5
print 'instagram:', qt5.qt_version

from instagram.qt.browser import InstagramView
from twisted.internet import reactor, defer, task

from app import keys, fixed
from amazon.dynamo import Tweet
import time
import sys

iw = InstagramView()
iw.show()    
iw.setFixedWidth(1024)
iw.setFixedHeight(768)

if len(sys.argv) > 1:
    gt = '%f' % ((time.time() - (3600 * 24 * int(sys.argv[1]))) * 1000)
if len(sys.argv) > 2:
    lt = '%f' % ((time.time() - (3600 * 24 * int(sys.argv[2]))) * 1000)

        
def fix_error(err, instagram):
    print 'fix error:', err
    try:
        del instagram[Tweet.instagrams]
    except:
        pass

def scan_all():
    kwargs = {}
    if len(sys.argv) > 1:
        kwargs['_ts_ms__gt'] = str( gt ).split('.')[0]
    if len(sys.argv) > 2:
        kwargs['_ts_ms__lt'] = str( lt ).split('.')[0]        
    kwargs['instagrams__null'] =  False
    print 'fix kwargs:', kwargs 
    return Tweet().scan(**kwargs)

def scan_partial():
    kwargs = {}
    kwargs['query_filter'] = { 'instagrams__null': False }
    #kwargs['index'] = Tweet.index_league
    #kwargs['league__eq'] = 'nfl'
    kwargs['index'] = Tweet.index_site
    kwargs['site__eq'] = 'd.com'
    return Tweet().query_2(**kwargs)            

@defer.inlineCallbacks
def bored_loop(seed = None):
    print 'bored loop:', seed
    for t in scan_all():
    #for t in scan_partial():
        print 'found:', t[keys.entity_league], t[keys.entity_twitter], 'length:', len(t['instagrams']), t[Tweet.tweet_user_id], t[Tweet.tweet_id]
        for instagram in t[Tweet.instagrams]:
            print 'instagram url:', instagram, 'lingo:', fixed.lingo_since_date(int(t[Tweet.ts_ms]) / 1000)
            yield iw.goto_url(instagram)
            yield iw.get_image_data(instagram, t).addErrback(fix_error, t)
            yield task.deferLater(reactor, 5, defer.succeed, True)            
            if t.needs_save():
                print 'needs save'
                t.partial_save()
    
def bored():
    iw.goto_url('https://www.google.com').addCallback(bored_loop)
       
if __name__ == '__main__':
    reactor.callWhenRunning(bored)
    reactor.run()
