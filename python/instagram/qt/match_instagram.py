import os
#os.environ['QTDISPLAY'] = ':2'
from qt import qt5
print 'instagram match:', qt5.qt_version

import time
import sys

yesterday = '%f' % ((time.time() - (3600 * 24)) * 1000)
skip_find = []

import pprint

from boto.dynamodb2.exceptions import ItemNotFound
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QTextEdit, QLineEdit, QTabWidget
from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

from twisted.internet import defer, reactor, task

from qt.view import ChromeView
import qtawesome as qta

from app import fixed
from amazon.dynamo import Tweet, Entity, ProfileTwitter
from twitter import twitter_keys
from app import keys
from instagram import instagram_keys

main_widget = QWidget()
main_widget.resize(1024, 768)
main_widget.setWindowTitle('Social Finder')
main_widget.setStyleSheet("background-color:black;")
main_widget.show()

tab_widget = QTabWidget(main_widget)
tab_widget.resize(1014, 200)
tab_widget.move(5,5)
tab_widget.show()

instagram_tab = QWidget()
tab_widget.resize(1014, 200)    
instagram_tab.setStyleSheet("background-color:black;")

twitter_label_html_fmt = """
    <html>
    <link rel="stylesheet" type="text/css" href="http://yui.yahooapis.com/3.18.1/build/cssreset/cssreset-min.css">
    <link href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet">
    <style>
    div.tw {
        margin-bottom:2px;
    }
    div.prefix::before {
        display: inline-block;
        width: 80px;
        content: attr(data-prefix) ":";
        font-size:.88em
    }
    .twitter {
        color: #0084b4;
        font-size: 1.5em;
    }
    </style>
    <body bgcolor="black">%s</body>
    </html>
"""

tab2 = QWidget()
tab2.setStyleSheet("background-color:white;")

twitter_info = QWebEngineView(instagram_tab)
twitter_info.setFixedWidth(714)
twitter_info.setFixedHeight(200)
twitter_info.setHtml(twitter_label_html_fmt % '')
twitter_info.show()

tab_widget.addTab(instagram_tab, qta.icon('fa.instagram', color='#fb3958'), "Instagram")
tab_widget.addTab(tab2, qta.icon('fa.twitter', color='#0084b4'), "Twitter")

match_button = QPushButton('Instagram Match', instagram_tab)
match_button.move(754, 20)
non_match_button = QPushButton('Not Instagram Match', instagram_tab)
non_match_button.move(754, 55)
found_button = QPushButton('Found', instagram_tab)
found_button.move(754, 90)

search_button = QPushButton('Search', instagram_tab)
search_button.move(884, 90)

ignore_button = QPushButton('Ignore Tweeter', instagram_tab)
ignore_button.move(754, 125)
next_button = QPushButton('Next Match', instagram_tab)
next_button.move(884, 125)

def twitter_label_html(entity):
    html = '<div style="background-color:#D3D3D3;position:absolute;width:714px;height:200px">'
    html += '<img align=left src=http://' + entity[keys.entity_site] + '/tw/' + entity[keys.entity_twitter_id] + '/avatar_large.png width=150  height=150 hspace=10 vspace=10>'
        
    html += '<div class="tw" style="padding:10px 0 4px 0"><i class="fa fa-twitter twitter"></i> <b style="font-size:1.116em">' + entity[keys.entity_twitter] + '</b></div>'
    if entity[keys.entity_name]:
        html += '<div class="tw prefix" data-prefix="Name">' + entity[keys.entity_name] + '</div>'
    html += '<div class="tw prefix" data-prefix="League">' + entity[keys.entity_league] + '</div>'
    if entity[keys.entity_team]:
        html += '<div class="tw prefix" data-prefix="Team">' + entity[keys.entity_team] + '</div>'
    elif entity[keys.entity_profile].startswith('team:'):
        html += '<div class="tw prefix" data-prefix="Team">' + entity[keys.entity_profile].split(':')[1] + '</div>'        
    if entity[keys.entity_jersey]:
        html += '<div class="tw prefix" data-prefix="Jersey"> #' + entity[keys.entity_jersey] + '</div>'
    if entity[keys.entity_position]:
        html += '<div class="tw prefix" data-prefix="Position">' + entity[keys.entity_position] + '</div>'
    html += '</div>'    
    twitter_info.setHtml(twitter_label_html_fmt % html)

def clean_match(tweet):
    del tweet[twitter_keys.match_posts]
    del tweet[twitter_keys.match_followers]
    del tweet[instagram_keys.instagram_avi]    
    del tweet[ProfileTwitter.following]
    del tweet[instagram_keys.instagram_url]
    del tweet[instagram_keys.instagram_verified]
    if tweet[Tweet.unknown_instagrams] and len(tweet[Tweet.unknown_instagrams]) == 1 and tweet[instagram_keys.instagram_name]:
        tweet[Tweet.unknown_instagrams][0][instagram_keys.instagram_name] = tweet[instagram_keys.instagram_name]
    del tweet[instagram_keys.instagram_name]
    tweet.partial_save()
    pprint.pprint(tweet._data)
    
def process_find(maybe_instagram, entity, t):
    if maybe_instagram:
        entity[keys.entity_instagram] = maybe_instagram
        instagram_keys.validate_instagram(entity)
        if entity.needs_save():
            entity.partial_save()
            skip_find.append(entity[keys.entity_twitter])
        if t:
            clean_match(t)

def process_match(entity = None, tweet = None):
    if entity is None:
        return
    if entity:        
        if not entity[keys.entity_instagram]:
            print 'no instagram!' 
            entity[keys.entity_instagram] = tweet[instagram_keys.instagram_name]
            instagram_keys.validate_instagram(entity)
            if entity.needs_save():
                entity.partial_save()
        u = tweet[Tweet.unknown_instagrams][0]
        if not tweet[Tweet.self_instagrams]:
            tweet[Tweet.self_instagrams] = []
        tweet[Tweet.self_instagrams].append(u)
        tweet[Tweet.unknown_instagrams].remove(u)
        if not tweet[Tweet.unknown_instagrams]:
            del tweet[Tweet.unknown_instagrams]
        if not tweet[keys.entity_instagram] or tweet[keys.entity_instagram] != entity[keys.entity_instagram]:
            tweet[keys.entity_instagram] = entity[keys.entity_instagram]
    if tweet:        
        clean_match(tweet)


attribute_list = [
    Tweet.ts_ms,
    Tweet.tweet_id,
    keys.entity_instagram,
    twitter_keys.match_posts,
    twitter_keys.match_followers,
    instagram_keys.instagram_avi,
    instagram_keys.instagram_name,
    ProfileTwitter.following,
    instagram_keys.instagram_url,
    instagram_keys.instagram_verified,
    Tweet.unknown_instagrams,
    Tweet.self_instagrams,
    keys.entity_league,
    keys.entity_profile,
    keys.entity_twitter,
    keys.entity_site,
    Tweet.tweet_user_id,
    keys.entity_team,
    keys.entity_name,
    keys.entity_jersey
]

def scan_all():
    kwargs = { 'unknown_instagrams__null' : False, 'instagram_name__null': False, "_ts_ms__gt": str( yesterday ), 'conditional_operator': 'AND'}
    kwargs['attributes'] = attribute_list
    return Tweet().scan(**kwargs)

def scan_league():
    return Entity().query_2(league__eq=sys.argv[1], query_filter={'instagram__null': True, 'twitter__null': False})

def hide_buttons():
    match_button.hide()
    non_match_button.hide()
    found_button.hide()
    ignore_button.hide()
    next_button.hide()
    search_button.hide()
    twitter_info.setHtml(twitter_label_html_fmt % '')
    instagram_tab.setStyleSheet("background-color:black;")
def show_buttons(t = None):
    if t:
        match_button.show()
    non_match_button.show()
    found_button.show()
    ignore_button.show()
    next_button.show()
    search_button.show()
    instagram_tab.setStyleSheet("background-color:#D3D3D3;")

cv = ChromeView(main_widget)
cv.setFixedWidth(1024)
cv.setFixedHeight(618)
cv.move(0, 210)
cv.show()

@defer.inlineCallbacks
def execute_find(origin_entity, t = None):
    if t and t[instagram_keys.instagram_name] is not None:
        yield cv.goto_url('https://www.instagram.com/' + t[instagram_keys.instagram_name])
    twitter_label_html(origin_entity)
    d = defer.Deferred()
    d.addCallback(process_match, t)                            
    def click_match():
        hide_buttons()
        try:
            entity = Entity().get_item(league=t[keys.entity_league], profile=t[keys.entity_profile])
            d.callback(entity)
        except ItemNotFound:
            print 'cannot find history'
            d.callback(False)
    def click_not_match():
        hide_buttons()                                
        d.callback(False) 
    def click_found():
        hide_buttons()
        if 'www.instagram.com' in cv.page().url().toString():
            found_instagram = cv.page().url().toString()[26:].split('/')[0]
            print 'found instagram:', found_instagram
            reactor.callLater(0, process_find, found_instagram, origin_entity, t)
        d.callback(None)
    def click_ignore():
        hide_buttons()
        skip_find.append(origin_entity[keys.entity_twitter])
        d.callback(False)
    def click_next():
        hide_buttons()
        d.callback(None)
        
    def search_for():
        url_fmt = 'https://www.google.com/search?&q=%s+instagram'
        n = origin_entity['name'].encode('ascii', 'ignore') if 'name' in origin_entity else origin_entity['profile'].split(':')[1].encode('ascii', 'ignore')
        try:
            search_url = str(url_fmt % '+'.join(n.split(' ')))
        except:
            qt5.app.clipboard().setText(origin_entity[keys.entity_name])                        
            search_url = str(url_fmt % '+'.join(qt5.app.clipboard().text().encode('utf8')))
        cv.goto_url(search_url)

    search_button.clicked.connect(search_for)
    match_button.clicked.connect(click_match)
    non_match_button.clicked.connect(click_not_match)
    found_button.clicked.connect(click_found)
    ignore_button.clicked.connect(click_ignore)
    next_button.clicked.connect(click_next)                    
    show_buttons(t)
    if not t:
        search_button.click()
    yield d 
    match_button.clicked.disconnect(click_match)
    non_match_button.clicked.disconnect(click_not_match)
    found_button.clicked.disconnect(click_found)
    ignore_button.clicked.disconnect(click_ignore)
    next_button.clicked.disconnect(click_next)
    search_button.clicked.disconnect(search_for)
    

@defer.inlineCallbacks
def find_instagrams():
    yield cv.goto_url('https://www.instagram.com')
    try:
        for t in scan_all():                
            origin_entity = Entity().get_item(league=t[keys.entity_league], profile=t[keys.entity_profile])
            since = fixed.lingo_since_date(int(t[Tweet.ts_ms]) / 1000)
            instagram_entity = None
            if t[instagram_keys.instagram_name]:
                for i_e in Entity().query_2(index=Entity.index_instagram_league, instagram__eq=t[instagram_keys.instagram_name], limit=1):
                    instagram_entity = i_e
            if not instagram_entity and origin_entity[keys.entity_instagram]:
                try:
                    print '{:10s}'.format('unknown'), '{:3d}'.format(since[1]), '{:5s}'.format(since[0]), '{:50s}'.format('https://www.instagram.com/' + origin_entity[keys.entity_instagram]), 'of', '{:50s}'.format('https://www.instagram.com/' + t[instagram_keys.instagram_name])
                except:
                    print ''
            elif instagram_entity and instagram_entity[keys.entity_twitter] == t[keys.entity_twitter]:
                print 'found self instagram user:', '{:3d}'.format(since[1]), '{:5s}'.format(since[0])
                reactor.callLater(0, process_match, instagram_entity, t)
            elif instagram_entity and instagram_entity[keys.entity_twitter] != t[keys.entity_twitter] and origin_entity[keys.entity_instagram]:
                print '{:10s}'.format('known'), '{:3d}'.format(since[1]), '{:5s}'.format(since[0]), '{:50s}'.format('https://www.instagram.com/' + origin_entity[keys.entity_instagram]), 'of', '{:50s}'.format('https://www.instagram.com/' + instagram_entity[keys.entity_instagram])
                if not t[Tweet.unknown_instagrams] and t[Tweet.unknown_instagrams] and len(t[Tweet.unknown_instagrams]) == 1:
                    t[Tweet.unknown_instagrams] = t[Tweet.unknown_instagrams]
                    del t[Tweet.unknown_instagrams]
                elif t[Tweet.unknown_instagrams] and len(t[Tweet.unknown_instagrams]) == 1:
                    del t[Tweet.unknown_instagrams]
                del t[instagram_keys.instagram_name]
                if t.needs_save():
                    t.partial_save()                                        
            elif not origin_entity[keys.entity_instagram] and t[keys.entity_twitter] not in skip_find:
                yield execute_find(origin_entity, t)                
            else:
                print 'something else!'   
    except ItemNotFound as e:
        pass
    except KeyError as e:
        print 'key error:', e
        pprint.pprint(t._data)
        yield defer.Deferred()
    except AttributeError as e:
        print 'attribute error:', e
        pprint.pprint(t._data)
        yield defer.Deferred()
    except Exception as e:
        print 'oh fuck:', e.__class__.__name__
        print e
        pprint.pprint(t._data)
        print ''
        pprint.pprint(origin_entity._data)
        yield defer.Deferred()

@defer.inlineCallbacks
def find_league_instagrams():
    yield cv.goto_url('https://www.instagram.com')
    try:
        for origin_entity in scan_league():
            yield execute_find(origin_entity)   
    except ItemNotFound as e:
        pass
    except KeyError as e:
        print 'key error:', e
        pprint.pprint(origin_entity._data)
        yield defer.Deferred()
    except AttributeError as e:
        print 'attribute error:', e
        pprint.pprint(origin_entity._data)
        yield defer.Deferred()
    except Exception as e:
        print 'oh fuck:', e.__class__.__name__
        print e
        print ''
        pprint.pprint(origin_entity._data)
        yield defer.Deferred()        
        
if __name__ == '__main__':
    if len(sys.argv) > 1:
        reactor.callWhenRunning(find_league_instagrams)
    else:
        reactor.callWhenRunning(find_instagrams)
    reactor.run()
