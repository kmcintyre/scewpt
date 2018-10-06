import os
os.environ['QTDISPLAY'] = ':2'
from qt import qt5
print 'chart:', qt5.qt_version

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QUrl

from amazon.dynamo import User, Tweet
from app import keys, user_keys
from twitter import tweets
from twitter import restful

import time
import copy

from twisted.internet import reactor, defer, task

@defer.inlineCallbacks
def run_charts():
    print 'run charts'
    gsi = Tweet().describe()['Table']['GlobalSecondaryIndexes']
    oil = [g for g in gsi if g['IndexName'] == Tweet.index_league][0]['ProvisionedThroughput']
    oil = { Tweet.index_league: { 'read': oil['ReadCapacityUnits'], 'write': oil['WriteCapacityUnits']}}
    nil = copy.deepcopy(oil)
    nil[Tweet.index_league]['read'] = 200
    oil[Tweet.index_league]['read'] = 20
    try:
        print 'increate throughput:', nil
        Tweet().update_global_secondary_index(global_indexes=nil)
    except Exception as e:
        print 'increase exception:', e
    yield task.deferLater(reactor, 15, defer.succeed, True)
    for u in User().scan(role__contains='.com', twitter_apps__null=False):
        try:
            site = u[user_keys.user_role]
            chart_tweet = tweets.chart_tweet(u, 'Last 24 Hours')
            print 'chart tweet:', chart_tweet
            yield task.deferLater(reactor, 1, defer.succeed, True)            
            print 'site:', site
            if not u[keys.entity_description]:
                u[keys.entity_description] = 'placeholder'
                u.partial_save()


            yesterday = int(time.time()) - (24 * 60 * 60)
            yesterday = str(yesterday * 1000)
            
            curator = User().get_by_role(site, keys.entity_twitter)
            charts = []
            
            categories = list(curator[user_keys.user_site_leagues])
            for c in categories:
                #tc = SocialBeta().query_count(SocialBeta.index_social_ts_received, league__eq=c, social_ts_received__gt=yesterday, query_filter={'social_act__eq': 'tweet'})
                tweet_filter={'known_retweet__null': True, 'unknown_retweet__null': True, '_ts_ms__gt' : yesterday}
                 
                tc = Tweet().query_count(index=Tweet.index_league, league__eq=c, query_filter=tweet_filter, scan_index_forward=False)
                
                
                known_retweet_filter={'known_retweet__null': False, '_ts_ms__gt' : yesterday}
                krc = Tweet().query_count(index=Tweet.index_league, league__eq=c, query_filter=known_retweet_filter, scan_index_forward=False)
                
                unknown_retweet_filter={'unknown_retweet__null': False, '_ts_ms__gt' : yesterday}
                urc = Tweet().query_count(index=Tweet.index_league, league__eq=c, query_filter=unknown_retweet_filter, scan_index_forward=False)
                
                conversion_filter={'known_conversation__null': False, '_ts_ms__gt' : yesterday}                
                cc = Tweet().query_count(index=Tweet.index_league, league__eq=c, query_filter=conversion_filter, scan_index_forward=False)                
                ce = { c: (tc, krc, urc, cc) }
                print ce
                charts.append(ce)            
                
            charts.sort(key=lambda x: x[x.keys()[0]][0])    
                
            tweets_list = [t[t.keys()[0]][0] for t in charts]
            known_retweets_list = [t[t.keys()[0]][1] for t in charts]
            unknown_retweets_list = [t[t.keys()[0]][2] for t in charts]
            conversations_list = [t[t.keys()[0]][3] for t in charts]
            categories = [t.keys()[0] for t in charts]        
            
            height = 200 + (40*len(categories))
            
            view = QQuickView() 
            view.setSource(QUrl('qml/render/chart_daily.qml'))
            view.setWidth(800) 
            view.setHeight(height)
            
            view.rootObject().setProperty('categories', categories)
            view.rootObject().setProperty('_height', height)
            view.rootObject().setProperty('title', 'Tweets/Retweets/Conversations - ' + site)
            view.rootObject().setProperty('description', u[keys.entity_description])
            view.rootObject().setProperty('conversations', conversations_list)
            view.rootObject().setProperty('retweets', known_retweets_list)
            view.rootObject().setProperty('unknown_retweets', unknown_retweets_list)
            view.rootObject().setProperty('tweets', tweets_list)
            
            view.show()
            yield task.deferLater(reactor, 5, defer.succeed, True)
            img = view.grabWindow();
            chart_location = '/home/ubuntu/Desktop/' + site + '.png'
            res = img.save(chart_location)
            print 'save result:', res
            yield task.deferLater(reactor, 5, defer.succeed, True)            
            restful.post_tweet(u, u, chart_tweet, chart_location)
            yield task.deferLater(reactor, 15, defer.succeed, True)
            os.remove(chart_location)
            view.deleteLater()                
            
        except Exception as e:
            print 'chart exception:', e
    try:
        print 'decreate throughput:', oil        
        Tweet().update_global_secondary_index(global_indexes=oil)
    except Exception as e:
        print 'descrease exception:', e    
    yield task.deferLater(reactor, 15, defer.succeed, True)
    reactor.callLater(0, reactor.stop)
if __name__ == '__main__':    
    reactor.callWhenRunning(run_charts)
    reactor.run()
