import os
from twitter import twitter_keys
os.putenv('DISPLAY', ':2')

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtWebEngineWidgets import QWebEngineView 
from PyQt5.QtCore import QTimer 

from app import keys, user_keys, fixed
from amazon.dynamo import User, Entity
from amazon.sqs import TweetQueue, BackgroundQueue
from amazon import s3

import random
import string
import simplejson as json
import sys

app = QApplication(sys.argv)

from qt import qt5reactor
print 'install qt5reactor'
qt5reactor.install()

from twisted.internet import reactor

background_html = """
    <!DOCTYPE html>
    <html>
    <style>
    body {{
         overflow:hidden;
    }}
    img {{
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        border-radius: 25px;
        border: 2px solid black;
    }}
    </style>
    <script>
    var bgs = [{0}];
    document.addEventListener("DOMContentLoaded", function(event) {{ 
        for (var x = bgs.length - 1; x >= 0; x--) {{
            var img = document.createElement("img");
            img.width = 570 - 25 * x;
            img.height = img.width / 3;
            img.setAttribute('src', bgs[x]);        
            img.style.zIndex = -x;
            var ty = 20 + 35 * x
            img.style.top = ty + 'px';
            document.body.appendChild(img);        
        }}
    }});
    </script>
    <body bgcolor="{1}"></body>
    </html>
"""


def background_pic(background, prefix = '/tmp'):
    print 'background:', background[keys.entity_league], 'http://twitter.com/' + background[keys.entity_twitter]
    curator = User().get_curator(background[keys.entity_league])
    bgs = s3.get_twitter_media(background, 'background')
    if len(bgs) > 10:
        print 'more than 10 backgrounds:', len(bgs)
        bgs = bgs[:10]
    bgstringarray = ['"' + fixed.key_url(s) + '"' for s in bgs]
    print bgstringarray
    bgstring = ','.join(bgstringarray)
    bgcolor = 'white'    
    cv = QWebEngineView()    
    cv.setFixedWidth(590)
    minheight = 210
    minwidth = 570
    for b in bgs:
        currentheight = minwidth / 3 
        minwidth = minwidth - 25
        newheight = minwidth / 3
        actual_diff = 35 + (newheight - currentheight)         
        minheight = minheight + actual_diff     
    cv.setFixedHeight(minheight)
    cv.show() 

    def html_loaded(result = None):
        print 'html_loaded:', result
        local_file_name = prefix + '/bg_update_' + background[keys.entity_twitter] + '.png'
        qimg = QImage(cv.width(), cv.height(), QImage.Format_ARGB32_Premultiplied)
        painter = QPainter(qimg)
        cv.page().view().render(painter)
        qimg.save(local_file_name)
        print 'saved:', local_file_name, 'painter:', painter, 'qimg:', qimg
        del painter
        if background and twitter_keys.message_tweet in background:
            upload_png = background[keys.entity_league] + '/tweet/' + ''.join(random.choice(string.ascii_lowercase) for _ in range(10)) + '.png'            
            b = s3.bucket_straight(curator['role'])            
            s3.save_s3(b, upload_png, None, local_file_name, 'image/png')
            bg_message_pic = 'http://' + b.name + '/' + upload_png    
            print 'bg_message_pic:', bg_message_pic
            if background:
                background[twitter_keys.message_pic] = bg_message_pic
                print 'append to tweet:', background[twitter_keys.message_tweet], 'url:', background[twitter_keys.message_pic]
                TweetQueue().createMessage(background)
        cv.close()
        reactor.stop()
        
    def post_load(result = None):
        print 'post load:', result
        QTimer.singleShot(10000, html_loaded)            
    
    cv.page().loadFinished.connect(post_load)   
    formatted_html = background_html.format(bgstring, bgcolor)
    cv.page().setHtml(formatted_html)

def check_background_queue():
    bq = BackgroundQueue()
    print 'check background queue:', bq
    msg = bq.getMessage()    
    try:
        background = json.loads(msg.get_body())
        background_pic(background)
        print 'delete background msg!'
        bq.deleteMessage(msg)                    
    except Exception as e:
        print 'no background messages', e
        reactor.callLater(60, reactor.stop)
            
if __name__ == '__main__':
    if len(sys.argv) == 1:
        reactor.callWhenRunning(check_background_queue)
    else:
        for e in Entity().query_2(index=Entity.index_twitter_league, twitter__eq=sys.argv[1]):
            print 'run:', 'https://twitter.com/' + sys.argv[1]
            reactor.callWhenRunning(background_pic, e._data)
    reactor.run()
