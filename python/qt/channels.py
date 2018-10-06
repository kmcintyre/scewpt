from PyQt5.QtCore import pyqtSlot, QObject

from app import fixed

import random
import string

from twisted.internet import defer

js_goto_bottom="""
while ( document.querySelectorAll('div.Grid-cell').length < parseInt(document.querySelector('li[data-element-term="follower_you_know_toggle"]').innerHTML.trim().split(' ')[0].replace(',','')) ) {
    window.scrollTo(0,document.body.scrollHeight);
} 
"""

class CommonAction(QObject):
    
    def js_script(self):
        return fixed.qwebchannel() + self.to_webpage()

class JsBottom(QObject):
    
    callback = None

    @pyqtSlot(str)
    def complete(self, bg_color):
        print 'JsBottom!', bg_color
        if self.callback:        
            self.callback.callback(bg_color)

class InstagramPositioningAction(CommonAction):

    callback = None
    
    action_name = "instagramPositioning"
    
    fmt_webpage = """
        try {
            if ( qt ) new QWebChannel(window.qt.webChannelTransport, function (channel) {
                var el = document.querySelector("article header + div img");
                if (el ) {
                    channel.objects.%s.complete( el.getBoundingClientRect().top, el.getBoundingClientRect().right, el.getBoundingClientRect().bottom, el.getBoundingClientRect().left );
                } else {                
                    channel.objects.%s.fail()
                }                        
            });
        } catch (err) {
            alert(err);
        }    
    """
    
    def to_webpage(self):
        return self.fmt_webpage % (self.action_name, self.action_name)

    @pyqtSlot(int, int, int, int)
    def complete(self, top, right, bottom, left):
        print 'channel instagram complete!', top, right, bottom, left
        self.callback.callback((top, right, bottom, left))

    @pyqtSlot()
    def fail(self):
        print 'channel failure instagram'
        self.callback.callback(False)

    def action(self):
        return self.action_name

        
class BgColorAction(CommonAction):

    callback = None

    action_name = "actionBgColor"
    
    fmt_webpage = """
        if ( qt ) new QWebChannel(window.qt.webChannelTransport, function (channel) {
            var bg = document.querySelector(".ProfileCanopy-header.u-bgUserColor");
            if (bg) {
                channel.objects.%s.complete(window.getComputedStyle(bg, null).getPropertyValue("background-color"));
            } else {
                channel.objects.%s.fail()                
            }            
        });    
    """ 
    
    def to_webpage(self):
        return self.fmt_webpage % (self.action_name, self.action_name)
    
    @pyqtSlot(str)
    def complete(self, bg_color):
        print 'channel bgcolor complete!', bg_color
        self.callback.callback(bg_color)

    @pyqtSlot()
    def fail(self):
        print 'channel failure no backgroud' 
        self.callback.errback(fixed.MissingBackground())

    def action(self):
        return self.action_name
    
    
class SuiLoadAction(CommonAction):

    callback = None

    action_name = "suiLoad"
    
    fmt_webpage = """
        console.log('HEY!');
        if ( qt ) new QWebChannel(window.qt.webChannelTransport, function (channel) {
            document.getElementById('wwsui-main-container').addEventListener('wwSuiWidgetLoadSuccess', function(evt) {
                channel.objects.%s.complete(true);
            });            
        });    
    """ 
    
    def to_webpage(self):
        return self.fmt_webpage % (self.action_name)
    
    @pyqtSlot(str)
    def complete(self, success):
        print 'channel success complete!', success
        self.callback.callback(success)

    @pyqtSlot()
    def fail(self):
        print 'channel failure' 
        self.callback.errback(Exception())

    def action(self):
        return self.action_name    