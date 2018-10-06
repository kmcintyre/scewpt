import os
#os.environ['QTDISPLAY'] = ':2'
from qt import qt5
print 'curator_background:', qt5.qt_version

from amazon.dynamo import User, Entity
from twitter import restful
from app import keys, user_keys

import sys

from twisted.internet import task, reactor, defer
from twisted.web.client import Agent
from amazon import s3

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QUrl

def screenshot(view, site, curator):
    img = view.grabWindow();
    il = '/home/ubuntu/' + site + '/curator_background.png'
    res = img.save(il)
    print 'save result:', res, il
    try:
        bs = s3.bucket_straight(curator[user_keys.user_role])
        s3.save_s3(
            bs
            ,
            'curator_background.png',
            None,
            il,
            'image/png',
            'public-read'
        )
    except Exception as e:
        print e
    curator = User().get_by_role(site, keys.entity_twitter)
    restful.update_background(curator, curator, il)    

def add_redirect(r, e, arr, size):
    if r.code == 301:
        url = [l for l in list(r.headers.getAllRawHeaders()) if l[0] == 'Location'][0][1][0]
        pd = {size + '_url': url}
        pd.update(e._data)
        arr.append(pd)
    
@defer.inlineCallbacks
def buildandsave(site, exit_on_save = True):
    agent = Agent(reactor)  
    curator = User().get_by_role(site, keys.entity_twitter)
    
    leagues = []
    deferreds_league =[]
    for l in curator[user_keys.user_site_leagues]:
        league = Entity().get_item(league=l, profile='league:' + l)
        d = agent.request("HEAD", str('http://' + league[keys.entity_site] + '/tw/' + league[keys.entity_twitter_id]  + '/avatar_large.png'))
        d.addCallback(add_redirect, league, leagues, 'large')            
        deferreds_league.append(d)
    yield defer.DeferredList(deferreds_league)
    print 'leagues length:', len(leagues)
        
    players = []
    deferreds_small = []  
    for p in Entity().query_2(index=Entity.index_site_profile, site__eq=curator[user_keys.user_role], query_filter={'twitter__null': False}, limit=200):
        d = agent.request("HEAD", str('http://' + p[keys.entity_site] + '/tw/' + p[keys.entity_twitter_id]  + '/avatar_small.png'))
        d.addCallback(add_redirect, p, players, 'small')            
        deferreds_small.append(d)
    yield defer.DeferredList(deferreds_small)
    print 'players length:', len(players)
    
    view = QQuickView() 
    view.setSource(QUrl('qml/render/curator_twitter_bg.qml'))
    view.rootObject().setProperty('bgcolor', 'black')
    view.setWidth(1500) 
    view.setHeight(500)
    view.show()
    view.rootObject().setProperty('curator', curator._data)
    view.rootObject().setProperty('leagues', leagues)
    view.rootObject().setProperty('players', players)
    
    yield task.deferLater(reactor, 30, screenshot, view, site, curator)
    if exit_on_save:
        print 'exit on save'
        reactor.callLater(0, reactor.stop)
    else:
        print 'done'

@defer.inlineCallbacks
def run_sites():
    for site in User().get_sites():
        print '    site:', site[user_keys.user_role]
        yield buildandsave(site[user_keys.user_role], False)
def error(err):
    print err
if __name__ == '__main__':
    if len(sys.argv) > 1:
        reactor.callWhenRunning(buildandsave, sys.argv[1])
    else:
        reactor.callWhenRunning(run_sites)
    reactor.run()
