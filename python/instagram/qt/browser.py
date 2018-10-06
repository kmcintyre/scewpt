from qt.view import ChromeView
from twisted.internet import defer, task, reactor

from app import fixed, keys, parse, misc
from amazon.dynamo import Tweet, Entity
from amazon import s3
from instagram import instagram_keys

import StringIO
import json
import urllib2
import subprocess

class InstagramView(ChromeView):

    def set_action(self, action, d):
        from PyQt5.QtWebChannel import QWebChannel
        self.page().setWebChannel(None)
        channel = QWebChannel(self.page())
        channel.registerObject(action.action(), action)
        self.page().setWebChannel(channel)
        action.callback = d

    def image_trim(self, localfile):
        from wand.image import Image
        with Image(filename=localfile) as img:
            img.trim()
            img.save(filename=localfile)

    def bundle_instagram(self, tweetplus, file_string):        
        try:
            io = StringIO.StringIO()
            json.dump(tweetplus, io, cls=fixed.SetEncoder)
            fixed_header = '{:5s}'.format(str(len(io.getvalue())))
            print 'bundle tweet', tweetplus[Tweet.tweet_id]
            return fixed_header + io.getvalue() + file_string
        except Exception as e:
            print 'bundle_instagram error:', e

    def clean_up(self, cu):
        for k in ['colors', 'ts_drop_prevented', 'ts_followers', 'ts_non_qualified', 'source_instagram', 'source_twitter']:
            for k2 in [k3 for k3 in cu.keys() if k3.startswith(k)]:
                del cu[k2]

    @defer.inlineCallbacks
    def get_image_data(self, url, tb):
        print 'get_image_data:', url
        yield task.deferLater(reactor, 1, defer.succeed, True)
        html = yield self.to_html()
        ig = {}
        if len(html.cssselect('div.error-container h2')) > 0:
            print 'remove url', tb
            tb[Tweet.instagrams].remove(url)
        else:            
            try:
                ig[instagram_keys.instagram_caption] = parse.csstext(html.cssselect('article div div ul li span')[0])
                print 'caption:', ig[instagram_keys.instagram_caption] 
            except:
                print 'no caption'
            verified = len(html.cssselect('span.coreSpriteVerifiedBadgeSmall[title="Verified"]')) > 0
            if verified:
                ig[instagram_keys.instagram_verified] = verified 
            instagram_name = html.cssselect('article header')[0].cssselect('div a')[0].attrib['href'][1:][:-1]
            print 'instagram name:', instagram_name
            article = html.cssselect('article header')[0]
            try:
                avi = fixed.clean_url(article.cssselect('span img')[0].attrib['src'])
            except:
                try:
                    avi = fixed.clean_url(article.cssselect('canvas + a img')[0].attrib['src'])
                except:
                    print 'missing avi?'
            print 'instagram avi:', avi
            ig[instagram_keys.instagram_avi] = avi 
            ig[instagram_keys.instagram_url] = url
            print ig
            found_instagram = False
            for k_instagram in Entity().query_2(index=Entity.index_instagram_league, instagram__eq=instagram_name):
                found_instagram = True
                if k_instagram[keys.entity_twitter_id] == tb[Tweet.tweet_user_id]:
                    if Tweet.self_instagrams not in tb or not tb[Tweet.self_instagrams]:
                        tb[Tweet.self_instagrams] = []
                    tb[Tweet.self_instagrams].append(ig)
                else:
                    ig.update(k_instagram._data)
                    self.clean_up(ig)
                    if Tweet.known_instagrams not in tb or not tb[Tweet.known_instagrams]:
                        tb[Tweet.known_instagrams] = []
                    tb[Tweet.known_instagrams].append(ig)
            if not found_instagram:
                tb[instagram_keys.instagram_name] = instagram_name
                if Tweet.unknown_instagrams not in tb or not tb[Tweet.unknown_instagrams]:
                    tb[Tweet.unknown_instagrams] = []
                tb[Tweet.unknown_instagrams].append(ig)                    
            
            tb[Tweet.instagrams].remove(url)
            if not tb[Tweet.instagrams]:
                del tb[Tweet.instagrams]
            try:
                if tb.needs_save():
                    tb.partial_save()
            except:
                pass
            print 'get_image_data complete:', ig    
        defer.returnValue(ig)
    
    def check_avatar(self, incoming, i):
        b = s3.bucket_straight('socialcss.com')
        filename = 'insta/' + incoming[keys.entity_instagram_id] + '/' +  fixed.digest(i[instagram_keys.instagram_avi]) + '.png'                
        if not s3.check_key(b, filename):
            local_large_avi_path = '/tmp/instagram/avi_' + incoming[keys.entity_instagram_id] + i[instagram_keys.instagram_avi][i[instagram_keys.instagram_avi].rindex('.'):]
            fixed.filesubpath(local_large_avi_path)
            with open(local_large_avi_path, 'w') as large_file:
                response = urllib2.urlopen(i[instagram_keys.instagram_avi]).read()
                large_file.write(response)
            if local_large_avi_path[-3:].lower() == 'jpg' or local_large_avi_path[-4:].lower() == 'jpeg':
                new_local_large_avi_path = '/tmp/large/png/' + incoming[keys.entity_instagram_id] + '.png'
                fixed.filesubpath(new_local_large_avi_path)
                args = ['convert', local_large_avi_path, new_local_large_avi_path]
                subprocess.check_call(args)
                local_large_avi_path = new_local_large_avi_path  
            misc.round_corners(local_large_avi_path, 'insta')                  
            e = Entity().get_item(league=incoming[keys.entity_league], profile=incoming[keys.entity_profile])    
            s3.save_insta_avi(i[instagram_keys.instagram_avi], local_large_avi_path, e._data)        
            
    @defer.inlineCallbacks
    def post_process(self, ig, incoming):
        from qt import qt5
        from qt.channels import InstagramPositioningAction
        from wand.image import Image
        
        location = '/tmp/instagram/temp_' + fixed.digest(ig[instagram_keys.instagram_url]) + '.png'            
        qt5.app.toImage(location)
        
        instagram_action = InstagramPositioningAction()
        instagram_d = defer.Deferred()
        self.set_action(instagram_action, instagram_d)
        self.page().runJavaScript(instagram_action.js_script())
        instagram_positioning = yield instagram_d        
        
        print 'instagram positioning:', instagram_positioning
        if instagram_positioning:        
            instagram_im = Image(filename=location)
            instagram_im.crop(left=instagram_positioning[3], top=instagram_positioning[0], right=instagram_positioning[1], bottom=instagram_positioning[2])
            instagram_clip = '/tmp/instagram/instagram_' + fixed.digest(ig[instagram_keys.instagram_url]) + '.png'
            instagram_im.save(filename=instagram_clip)  
            
            print 'send_image:', instagram_clip
            try:
                io = StringIO.StringIO(open(instagram_clip, 'r').read()).getvalue()
                fi = self.bundle_instagram(incoming._data, io)
                print 'send mime:', len(io)
                self.protocol.sendMessage(fi, True)
            except Exception as e:
                print 'send image exception:', e
        if Tweet.self_instagrams in incoming:            
            for i in incoming[Tweet.self_instagrams]:
                self.check_avatar(incoming, i)                                                
        elif Tweet.known_instagrams in incoming:
            for i in incoming[Tweet.known_instagrams]:
                self.check_avatar(i, i)

    
login_js = """
    document.querySelector('a[href="/accounts/login/"]').click()
"""
username_js="""
    document.querySelector('input[name="username"]').click();    
"""

if __name__ == '__main__':
    from PyQt5.QtTest import QTest
    from PyQt5.QtCore import Qt
    from qt import qt5
    iv = InstagramView()
    iv.setFixedWidth(1024)
    iv.setFixedHeight(768)
    iv.show()
    
    @defer.inlineCallbacks
    def enter_credentials():
        yield task.deferLater(reactor, 1, defer.succeed, True)
        print 'got here:', qt5.app.opengl
        #
        QTest.keyClick(qt5.app.opengl, Qt.Key_Tab, Qt.NoModifier, 10)
        QTest.keyClicks(qt5.app.opengl, 'again@mailvelo.com', Qt.NoModifier, 10)
        QTest.keyClick(qt5.app.opengl, Qt.Key_Tab, Qt.NoModifier, 100)
        QTest.keyClicks(qt5.app.opengl, 'Tererdfcv1!I', Qt.NoModifier, 10)
        QTest.keyClick(qt5.app.opengl, Qt.Key_Tab, Qt.NoModifier, 100)
        QTest.keyClick(qt5.app.opengl, Qt.Key_Tab, Qt.NoModifier, 100)
        QTest.keyClick(qt5.app.opengl, Qt.Key_Enter, Qt.NoModifier, 100)
        #QTest.keyClick(qt5.app.opengl, Qt.Key_Tab, Qt.ShiftModifier, 10)
        #QTest.keyClick(qt5.app.opengl, Qt.Key_Tab, Qt.NoModifier, 10)
    
    @defer.inlineCallbacks
    def username_focus():
        yield task.deferLater(reactor, 1, defer.succeed, True)
        iv.page().runJavaScript(username_js, lambda ign: enter_credentials() )
        
    @defer.inlineCallbacks
    def goto_instagram():
        yield iv.goto_url('https://www.instagram.com')
        iv.page().runJavaScript(login_js, lambda ign: username_focus() )
        #
        
        
    reactor.callWhenRunning(goto_instagram)
    reactor.run()
