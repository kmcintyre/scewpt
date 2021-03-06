from qt import qt5
print 'view:', qt5.qt_version
 
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile, QWebEngineSettings
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QUrl

from app import fixed, parse


from lxml import etree
from lxml.cssselect import CSSSelector

import random
import string
import pprint
import os
import urlparse
import re
import urllib

from twisted.internet import defer, reactor, task

class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    
    printable = []
    
    def status(self, info):
        print '{:15s}'.format(info.requestMethod()), info.requestUrl().toString()
        
    def interceptRequest(self, info):
        ru = info.requestUrl().toString()
        if len([p for p in self.printable if p in ru]) > 0:
            self.status(info)        
        #pass                

defaultRequestInterceptor = WebEngineUrlRequestInterceptor()

class ChromeView(QWebEngineView):
    
    def __init__(self, parent = None, page = None, fresh = True, storage_subdir = None, finish = None, javascript = None):
        super(ChromeView, self).__init__(parent)
        if page is not None:
            self.setPage(page)                    
        self.deferred_cbs = []        
        if fresh:
            if not storage_subdir:
                storage_subdir = ''.join(random.choice(string.ascii_lowercase) for _ in range(6))
            cache = '/' + fixed.tmp_disk + '/' + storage_subdir + '/cache'
            storage = '/' + fixed.tmp_disk + '/' + storage_subdir + '/storage'  
            os.makedirs(storage)
            os.makedirs(cache)
            self.page().profile().setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
            self.page().settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, False)
            self.page().profile().setCachePath(cache)
            self.page().profile().setPersistentStoragePath(storage)
        if javascript == False:
            self.page().settings().setAttribute(QWebEngineSettings.JavascriptEnabled, False)
        #pprint.pprint({'cookies:' : self.page().profile().persistentCookiesPolicy(), 'cache:' : self.page().profile().cachePath(), 'storage:' : self.page().profile().persistentStoragePath(), 'off the record:': self.page().profile().isOffTheRecord()})        
        if not finish:
            self.page().loadFinished.connect(self.finished)
        else:
            self.custom_finish = finish
            self.page().loadFinished(self.custom_finish)
        self.page().profile().setRequestInterceptor(defaultRequestInterceptor)

    def set_action(self, action, d):
        self.page().setWebChannel(None)
        channel = QWebChannel(self.page())
        channel.registerObject(action.action(), action)
        self.page().setWebChannel(channel)
        action.callback = d

    def qt_error(self, err):
        print 'qt err:', err, err.__class__.__name__
        reactor.stop()        
    
    def started(self):        
        print 'started ok'

    def progress(self, p):        
        print 'progress:', p
            
    def finished(self, ok):
        #print 'finished-', ok, len(self.deferred_cbs), self.page()
        for deferred in self.deferred_cbs:
            if not deferred.called:
                if not ok:
                    print 'not okay return:', ok, self.page().url().toString()
                deferred.callback(ok)
                return
    
    @defer.inlineCallbacks
    def to_html(self, ok = None, dumpit = None):
        if ok is not None:
            #print 'to_html ok?:', ok, self.page().url().toString()
            pass
        d = defer.Deferred()
        d.addCallback(etree.HTML)
        self.page().toHtml(lambda h: d.callback(h))
        html = yield d
        if dumpit:
            parse.dumpit(html, dumpit)
        defer.returnValue(html)
        
    @defer.inlineCallbacks
    def to_string(self, ok = None, dumpit = None):
        if ok is not None:
            #print 'to_html ok?:', ok, self.page().url().toString()
            pass
        d = defer.Deferred()        
        self.page().toHtml(lambda h: d.callback(h))
        html = yield d
        defer.returnValue(html)
        
    def renderProcessTerminated(self, renderProcessTerminationStatus, exitCode):
        print 'renderProcessTerminationStatus:', renderProcessTerminationStatus, 'exitCode:', exitCode
        reactor.stop()        

    def fmt_search_term(self, search_term):
        append_term = ''
        try:
            append_term = urllib.quote_plus(search_term.encode('utf8'))
        except:
            print 'USE QT!'
            qt5.app.clipboard().setText(search_term)
            st = qt5.app.clipboard().text()
            append_term = urllib.quote_plus(st.encode('utf8'))
        return append_term

    def bing(self, search_term, natural_delay = 4, results=1, domain=None, exclude=None):
        url = "http://www.bing.com/search?q=" + self.fmt_search_term(search_term)
        d = self.goto_url(url)
        d.addCallback(lambda ign: task.deferLater(reactor, natural_delay, self.to_html))
        d.addCallback(self.bing_cites, results, domain, exclude)
        return d        
    
    def google(self, search_term, natural_delay = 4, results=1, domain=None, exclude=None):
        url = "https://www.google.com/search?client=ubuntu&channel=fs&q=" + self.fmt_search_term(search_term)
        d = self.goto_url(url)
        d.addCallback(lambda ign: task.deferLater(reactor, natural_delay, self.to_html))
        d.addCallback(self.google_cites, results, domain, exclude)
        return d

    def bing_cites(self, html, results, domain, exclude):
        raw_cites = []        
        css = CSSSelector('ol[id="b_results"] li[class="b_algo"] h2 a')

        for anchor in css(html):
            try:
                raw_cites.append(anchor.attrib['href'])
            except:
                pass
        return self.filter_cites(raw_cites, results, domain, exclude)

    def google_cites(self, html, results, domain, exclude):
        css = CSSSelector('div[role="heading"]')
        for news in css(html):
            if etree.tostring(news, method="text", encoding='UTF-8').strip() == 'In the news':
                print 'clearing news'
                news.clear() 
        raw_cites = [etree.tostring(cite, method='text', encoding='UTF-8') for cite in html.findall('.//cite')]
        return self.filter_cites(raw_cites, results, domain, exclude)        
     
    def filter_cites(self, raw_cites, results, domain, exclude):            
        cites = []
        for cite in raw_cites:
            try:
                clean_cite = ''
                try:
                    clean_cite = cite.encode("utf8")
                except:
                    qt5.app.clipboard().setText(cite)
                    clean_cite = qt5.app.clipboard().text()                                        
                simple_cite = fixed.simpleurl(clean_cite.encode("utf8"))
                if domain is None or urlparse.urlparse(simple_cite).netloc == domain:
                    if exclude:
                        for pe in exclude:
                            if re.search(pe, simple_cite).group(1):
                                pass
                            else:
                                print 'accept:', simple_cite
                    try:
                        if '.' in simple_cite:
                            cites.append(simple_cite)
                    except Exception as e:
                        print 'inside exception:', e
            except Exception as e:
                print 'extract cite exception:', e
        if len(cites) > results:
            return cites[:results]
        return cites

    def goto_url(self, url):
        #print 'goto url:', url, len(self.deferred_cbs), self.page()
        qurl = QUrl(url)        
        d = defer.Deferred()
        self.deferred_cbs.append(d)     
        self.page().load(qurl)
        return d

    trans_focus = """
        document.querySelector('textarea[id="tw-source-text-ta"]').focus()    
    """    
    def google_translate(self):
        d = self.goto_url('https://www.google.com/search?client=ubuntu&channel=fs&q=google+translate')
        d.addCallback(lambda res: task.deferLater(reactor, 1, defer.succeed, res) )
        d.addCallback(lambda ign: self.page().runJavaScript(self.trans_focus) )
        d.addCallback(lambda res: task.deferLater(reactor, 1, defer.succeed, res) )
        d.addCallback(lambda res: self.page().triggerAction(QWebEnginePage.Paste)   )
        d.addCallback(lambda res: task.deferLater(reactor, 1, defer.succeed, res) )
        d.addCallback(self.to_html)
        d.addCallback(lambda trans_html: parse.csstext(trans_html.cssselect('div[id="tw-target-text-container"][class="tw-ta-container tw-nfl"] pre[data-placeholder="Translation"] span')[0]))
        return d 

    def error_view(self, err, err2 = None):
        print 'error_view:', err, err2

def started(chrome, url, cv):
    print 'started'
    if cv:
        window.page().loadStarted.connect(start_video)
    chrome.load(QUrl(url))
    
def start_video():
    qt5.app.toVideo(24)
    
if __name__ == '__main__':   
    window = ChromeView()
    window.show()
    window.setFixedWidth(1024)
    window.setFixedHeight(768)    
    url = "http://athleets.com"
    import sys
    if len(sys.argv) > 1:        
        url = sys.argv[1]
        if not urlparse.urlparse(url).scheme:
            if not sys.argv[1].startswith('chrome'):
                url = "http://" + sys.argv[1]
    capture_video = False
    if len(sys.argv) > 2:
        capture_video = True        
    print url    
    reactor.callWhenRunning(started, window, url, capture_video)
    
    reactor.run()