import os
os.putenv('DISPLAY', ':2')
from PyQt5 import QtWebEngineWidgets 
import sys

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtGui import QGuiApplication

from amazon.dynamo import ProfileTwitter, User, Entity
from amazon.sqs import TweetQueue, AvatarQueue
from amazon import s3
from app import fixed, keys, user_keys, time_keys

from twitter import twitter_keys 

import simplejson as json
import time

app = QGuiApplication(sys.argv)

from qt import qt5reactor
print 'install qt5reactor'
qt5reactor.install()

from twisted.internet import reactor

def qt_avatar(avi = None, prefix = '/tmp'):
    print 'new avatar:', avi[keys.entity_twitter], 'twitter id:', avi[keys.entity_twitter_id]
    meta = {}
    curator = User().get_curator(avi[keys.entity_league])
    previous = None
    try:
        avis = s3.get_twitter_media(avi,'large')
        count = str(len(avis))
        current = fixed.key_url(avis[0])        
        previous = fixed.key_url(avis[1])                
    except Exception as e:
        print e    
    print current, 'count:', count, 'previous:', previous
    bgcolor = 'black'
    local_font = 'http://socialcss.com/Roboto-Regular.ttf?raw=true'
    site = curator[user_keys.user_role]
    
    friends = []    
    try:
        ls = ProfileTwitter().profile_last(avi[keys.entity_twitter_id])
        meta.update(ls._data)
        print 'has recent:', fixed.days_since(ls, time_keys.ts_add) if ls else None
        if ls[ProfileTwitter.profile_background_color]:        
            bgcolor = '#' + ls[ProfileTwitter.profile_background_color]
            print 'colors background:', bgcolor, 'link profile:', ls['profile_link_color']            
        for f in list(ls[twitter_keys.league_follows(avi[keys.entity_league])].intersection(ls[twitter_keys.league_mutual(avi[keys.entity_league])])):
            friends.append(f)
        print 'friend:', friends
    except Exception as e:
        print 'avatar exception:', e
    
    meta.update(avi)
    
    view = QQuickView()
    view.setSource(QUrl('qml/render/avi_update.qml'))
    view.show()
    
    view.setWidth(590)
    view.rootObject().setProperty('current', current)
    if previous:
        view.rootObject().setProperty('previous', previous)
    view.rootObject().setProperty('bgcolor', bgcolor)
    view.rootObject().setProperty('font', local_font)
    view.rootObject().setProperty('site', site)
    view.rootObject().setProperty('count', count)
    view.rootObject().setProperty('league', avi[keys.entity_league])
    view.rootObject().setProperty('twitter', avi[keys.entity_twitter])
    if friends:
        view.setHeight(380)
        view.rootObject().setProperty('friends', json.dumps(friends))
    else:
        view.setHeight(280)
        
    local_file_name = prefix + '/avi_update_' + avi[keys.entity_twitter] + '.png'
    print 'local_file_name:', local_file_name
    
    def tick():
        try:
            upload_png = avi[keys.entity_league] + '/tweet/' + str(int(time.time())) + '.png'
            img = view.grabWindow()
            print 'img:', img, local_file_name, img.isNull()
            render_res = img.save(local_file_name)
            print 'render_res:', render_res, 'file name:', upload_png, 'tweet:', avi 
            if render_res and avi and twitter_keys.message_tweet in avi:
                b = s3.bucket_straight(curator['role'])                         
                s3.save_s3(b, upload_png, None, local_file_name, 'image/png', 'public-read', meta)
                if avi:
                    
                    avi[twitter_keys.message_pic] = 'http://' + b.name + '/' + upload_png
                    print 'append to tweet:', avi[twitter_keys.message_tweet], 'url:', avi[twitter_keys.message_pic]
                    TweetQueue().createMessage(avi)
            else:
                print 'skip publish'
        except Exception as e:
            print 'tick exception:', e
        reactor.callLater(0, reactor.stop)                                
        
    QTimer.singleShot(15000, tick)
    
def check_avatar_queue():
    aq = AvatarQueue()
    print 'check avatar queue:', aq
    msg = aq.getMessage()    
    try:
        avatar = json.loads(msg.get_body())
        qt_avatar(avatar)
        print 'delete avatar msg!'
        aq.deleteMessage(msg)            
    except:            
        print 'no avatar messages'
        reactor.callLater(60, reactor.stop)        
    
if __name__ == '__main__':
    if len(sys.argv) == 1:
        reactor.callWhenRunning(check_avatar_queue)
    else:
        for e in Entity().query_2(index=Entity.index_twitter_league, twitter__eq=sys.argv[1]):
            print 'run:', 'https://twitter.com/' + sys.argv[1]
            reactor.callWhenRunning(qt_avatar, e._data)        
    reactor.run()
