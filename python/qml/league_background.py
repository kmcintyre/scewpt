import os
#os.environ['QTDISPLAY'] = ':2'
from qt import qt5
from compiler.pycodegen import EXCEPT
print 'twitter_bg:', qt5.qt_version

from amazon.dynamo import User, UserAvailable, Entity
from twitter import restful
from app import fixed, keys, user_keys

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QUrl

import os
import json
import sys

from twisted.internet import task, reactor, defer
from twisted.web.client import Agent

def screenshot(view, league_user):
    try:
        img = view.grabWindow();
        il = '/home/ubuntu/Desktop/bg_' + league_user[user_keys.user_role] + '.png'
        res = img.save(il)
        print 'save result:', res
        restful.update_background(league_user, league_user, il)
    except Exception as e:
        print 'screenshot exception:', e
    
def add_redirect(r, e, arr, size):
    if r.code == 301:
        url = [l for l in list(r.headers.getAllRawHeaders()) if l[0] == 'Location'][0][1][0]
        pd = {size + '_url': url}
        pd.update(e._data)
        arr.append(pd)

@defer.inlineCallbacks
def buildandsave(league_name, exit_on_save = True):
    try:
        agent = Agent(reactor)
        league_user = User().get_by_role(league_name, keys.entity_twitter)
        print 'league_user:', league_user._data
        
        league = Entity().get_league(sys.argv[1])._data
        
        teams = []
        deferreds_team = []
        for t in Entity().query_2(league__eq=sys.argv[1], profile__beginswith='team:', query_filter={'twitter__null': False, 'twitter_id__null': False}):
            d = agent.request("HEAD", str('http://' + t[keys.entity_site] + '/tw/' + t[keys.entity_twitter_id]  + '/avatar_large.png'))
            d.addCallback(add_redirect, t, teams, 'large')            
            deferreds_team.append(d)
        yield defer.DeferredList(deferreds_team)
            
        players = []
        deferreds_small = []    
        for p in Entity().query_2(league__eq=sys.argv[1], profile__beginswith='http:', query_filter={'twitter__null': False, 'twitter_id__null': False}, limit=300):
            d = agent.request("HEAD", str('http://' + p[keys.entity_site] + '/tw/' + p[keys.entity_twitter_id]  + '/avatar_small.png'))
            d.addCallback(add_redirect, p, players, 'small')            
            deferreds_small.append(d)
        yield defer.DeferredList(deferreds_small)
        print 'players length:', len(players)
    
        view = QQuickView() 
        view.setSource(QUrl('qml/render/league_twitter_bg.qml'))
        view.setWidth(1500) 
        view.setHeight(500)
        view.show()
    
        try:
            view.rootObject().setProperty('bgcolor', '#' + league_user[keys.entity_colors][0])
        except:
            view.rootObject().setProperty('bgcolor', '#000000')
        view.rootObject().setProperty('league', league)
        view.rootObject().setProperty('players', players)
        view.rootObject().setProperty('teams', teams)
            
        yield task.deferLater(reactor, 30, screenshot, view, league_user)
        if exit_on_save:
            print 'exit on save'
            reactor.callLater(0, reactor.stop)
        else:
            print 'done'
    except Exception as e:
        print 'build and save exception:', e

    
@defer.inlineCallbacks
def run_leagues():
    for site in User().get_sites():
        print '    site:', site[user_keys.user_role]
        for league_name in site[user_keys.user_site_leagues]:
            yield buildandsave(league_name, False)    
    reactor.callLater(0, reactor.stop)
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        reactor.callWhenRunning(buildandsave, sys.argv[1], True)
    else:
        reactor.callWhenRunning(run_leagues)
    reactor.run()