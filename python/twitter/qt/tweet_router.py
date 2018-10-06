import os
os.environ['QTDISPLAY'] = ':2'
from qt import qt5
print 'route tweet:', qt5.qt_version

from twitter.qt.browser import TwitterView

from twitter import twitter_keys, auth

from amazon.sqs import TweetQueue
from amazon.dynamo import User
from twitter import restful
from app import keys, parse, user_keys

from PyQt5.QtWebEngineWidgets import QWebEnginePage

from twisted.internet import defer, reactor, task

import time
import json
import urllib

js_key="""
document.querySelector('button.js-global-new-tweet').click();  
"""

tweet_delay = {}

class TweetView(TwitterView):

    @defer.inlineCallbacks
    def getTweetKit(self, msg):
        if self.page().url().toString() == 'http://twitter.com':
            yield self.goto_url('http://twitter.com')
            
        qt5.app.clipboard().setText(msg)
        self.page().runJavaScript(js_key)
        yield task.deferLater(reactor, 1, defer.succeed, True)
        
        self.page().triggerAction(QWebEnginePage.SelectAll)
        self.page().triggerAction(QWebEnginePage.Paste)                
        
        yield task.deferLater(reactor, 1, defer.succeed, True)
        html = yield self.to_html()
        while len(html.cssselect('span[class="tweet-counter superwarn max-reached"]')) > 0:        
            print 'bad:', parse.csstext(html.cssselect('span[class="tweet-counter superwarn max-reached"]')[0])
            msg = msg.rsplit(' ', 1)[0]
            qt5.app.clipboard().setText(msg)
            self.page().triggerAction(QWebEnginePage.SelectAll)
            self.page().triggerAction(QWebEnginePage.Paste)                
            yield task.deferLater(reactor, .5, defer.succeed, True)
            html = yield self.to_html()
        parse.dumpit(html, '/tmp/tweet_trim.html')
        defer.returnValue(msg)        
    
    def trimIt(self, it, tweet, msg):    
        if tweet[twitter_keys.message_tweet] != it:
            tweet[twitter_keys.message_tweet] = it
        if keys.entity_site in tweet:
            try:
                user = User().get_by_role(tweet[keys.entity_league], keys.entity_twitter)            
                user_app = auth.user_app(user)
                print 'user:', user[user_keys.user_role]
                if user_app and not user[user_keys.user_locked]:
                    if tweet[keys.entity_league] not in tweet_delay or tweet_delay[tweet[keys.entity_league]] < int(time.time()) - 105:
                        print 'publish api tweet'                        
                        tweet_delay[tweet[keys.entity_league]] = int(time.time())                    
                        local_image_location = None
                        if twitter_keys.message_pic in tweet:
                            local_image_location = '/tmp/' + tweet[twitter_keys.message_pic].rsplit('/', 1)[1]
                            urllib.urlretrieve(tweet[twitter_keys.message_pic], local_image_location)
                        restful.post_tweet(user, user_app, tweet[twitter_keys.message_tweet], local_image_location)
                        TweetQueue().deleteMessage(msg)
                    else:
                        print 'delay publish api tweet'
                else:
                    print 'publish queue tweet'
                    TweetQueue(tweet[keys.entity_league]).createMessage(tweet)
                    TweetQueue().deleteMessage(msg)
            except Exception as e:
                print 'post tweet exception:', e
        else:
            print 'delete tweet'
            TweetQueue().deleteMessage(msg)
        
    def error_route(self, err):
        print 'error route:', err
        reactor.stop()
        
    def tweet(self, ign = None):
        msg = TweetQueue().getMessage()
        if msg is None:
            print 'wait 60 seconds'
            reactor.callLater(60, self.tweet)
            return
        tweet = json.loads(msg.get_body())
        print 'message:', tweet
        if twitter_keys.message_tweet in tweet and len(tweet[twitter_keys.message_tweet]) > 0:
            d = self.getTweetKit(tweet[twitter_keys.message_tweet])
            d.addCallback(self.trimIt, tweet, msg)
            d.addErrback(self.error_route)
            d.addBoth(lambda ign: reactor.callLater(10, self.tweet))
        else:
            print 'dump it!'
            TweetQueue().deleteMessage(msg)
            reactor.callLater(0, self.tweet)    

if __name__ == '__main__':
    tv = TweetView()
    tv.user = User().get_by_role('me', keys.entity_twitter)    
    tv.role = ('tweet', 'me')
    tv.show()
    tv.signin()
    reactor.run()
