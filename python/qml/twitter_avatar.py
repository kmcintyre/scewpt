from qt import qt5
print 'twitter_bg:', qt5.qt_version

from amazon.dynamo import User, UserAvailable, Entity
from twitter  import restful
from app import fixed, keys

import os
import json
import sys

league_user = User().get_by_role(sys.argv[1], keys.entity_twitter)
print 'league_user:', league_user._data
league = Entity().get_league(sys.argv[1])._data
cards = []
for t in Entity().query_2(league__eq=sys.argv[1], profile__beginswith='team:'):
    if t[keys.entity_twitter]:
        cards.append(t._data)
if len(cards) == 0:
    for t in Entity().query_2(league__eq=sys.argv[1], profile__beginswith='http:', query_filter={'twitter__null': False}, limit=30):
        if t[keys.entity_twitter]:
            cards.append(t._data)
            
curator = User().get_curator(sys.argv[1])

'''


print league

    
players = []     
for p in Entity().query_2(league__eq=sys.argv[1], profile__beginswith='http:', query_filter={ 'twitter__null': False}, limit=400):
    players.append(p._data)
'''

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QUrl

view = QQuickView() 
view.setSource(QUrl('qml/render/twitter_avatar.qml'))
#view.rootObject().setProperty('bgcolor', '#' + league_user[keys.entity_colors][0])
view.rootObject().setProperty('league', league)
#view.rootObject().setProperty('players', players)
view.rootObject().setProperty('cards', cards)
view.setWidth(400) 
view.setHeight(400)
view.show()
print view.rootObject()

from twisted.internet import task, reactor, defer

def backup():
    view.rootObject().setProperty('backup', True)
    league_backup = UserAvailable().get_by_role(sys.argv[1], keys.entity_twitter)
    if league_backup:
        img = view.grabWindow();
        il = '/home/ubuntu/Desktop/avatar_' + sys.argv[1] + '_backup.png'
        res = img.save(il)
        print 'save result:', res
        restful.update_avatar(league_backup, curator, il)
        os.remove(il)

def screenshot():
    img = view.grabWindow();
    il = '/home/ubuntu/Desktop/avatar_' + sys.argv[1] + '.png'
    res = img.save(il)
    print 'save result:', res
    restful.update_avatar(league_user, curator, il)
    os.remove(il)
    backup()
      

task.deferLater(reactor, 20, screenshot).addCallback(lambda ign: qt5.signalDown(None, None))
reactor.run()