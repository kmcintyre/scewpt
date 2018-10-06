from twisted.internet import reactor, defer, task

from league import league_shared, keys_market
from twitter import twitter_keys

from app import keys, fixed, parse
from lxml.html import soupparser

import requests

class CRYPTO(league_shared.SharedLeague):
    
    min_size = 1100
    max_size = 1300
    
    @defer.inlineCallbacks
    def getICOs(self):
        html = yield self.cv.goto_url('https://coinmarketcap.com/all/views/all/').addCallback(self.cv.to_html)
        trs = html.cssselect('div.table-responsive.compact-name-column div.dataTables_wrapper.no-footer table tr')
        icos = []
        for tr in trs[1:][:1200]:
            
            name = parse.csstext(tr.cssselect('a.currency-name-container')[0])
            rank = parse.csstext(tr[0])
            symbol = parse.csstext(tr.cssselect('td.col-symbol')[0])            
             
            try:
                href = tr.cssselect('span.currency-symbol a')[0].attrib['href']
                profile = fixed.clean_url('http://coinmarketcap.com' + href)
                
                print 'rank:', rank, 'name:', name, 'sybol:', symbol
                ico = { keys.entity_name: name, keys.entity_profile: profile, keys_market.symbol: symbol, keys.entity_rank: rank}
                
                try:
                    market_cap = twitter_keys.numTwitter( int(parse.csstext(tr.cssselect('td.no-wrap.market-cap.text-right')[0]).replace('$', '').replace(',', '').strip()) )
                    ico[keys.entity_market_cap] = market_cap
                except:
                    pass
                try:
                    supply = twitter_keys.numTwitter( int(parse.csstext(tr.cssselect('td.no-wrap.text-right.circulating-supply')[0]).replace('*', '').replace(',', '').strip()) )
                    ico[keys.entity_circulating_supply] = supply
                except:
                    pass
                
                icos.append(ico)
            except:
                pass            
        defer.returnValue(icos)            
    
    def innerHtml(self, frag, ico):
        frame_html = soupparser.fromstring(frag)
        frame_anchor = frame_html.cssselect('h1.timeline-Header-title.u-inlineBlock a.customisable-highlight')[0]
        twitter = parse.csstext(frame_anchor).split('@')[1]
        if twitter:
            ico[keys.entity_twitter] = twitter
    
    def innerHtmlError(self, err):
        print 'inner html error:', err    
    
    @defer.inlineCallbacks
    def icoSocial(self):
        icos = yield self.getICOs()
        for ico in icos:
            print 'ico:', ico[keys.entity_profile]
            yield self.cv.goto_url(ico[keys.entity_profile] + '#social')
            yield task.deferLater(reactor, 5, defer.succeed, True)
            html = yield self.cv.to_html()
            ico[keys.entity_name] = html.cssselect('h1[class="details-panel-item--name"] img')[0].attrib['alt']
            print 'entity name:', ico[keys.entity_name] 
            d = defer.Deferred()
            d.addCallback(self.innerHtml, ico)            
            d.addErrback(self.innerHtmlError)
            self.cv.page().runJavaScript('function tweeter() { return document.getElementById("twitter-widget-0").contentDocument.body.innerHTML; } tweeter();', d.callback)            
            yield d
            if keys.entity_twitter in ico.keys():
                print 'twitter:', ico[keys.entity_twitter]
            else:
                print 'no twitter!'
        defer.returnValue(icos)            

    def filter_tweet(self, msg):
        if len([k for k in msg if '__' in k]) == 2 and 'rank__change' in msg and 'market_cap__change' in msg:
            return True
        elif len([k for k in msg if '__' in k]) == 1 and ('rank__change' in msg or 'market_cap__change' in msg):
            return True
        return False
            
    @defer.inlineCallbacks    
    def entities(self):
        cryptos = []
        try:
            icos = yield self.icoSocial()
            cryptos.extend(icos)
        except Exception as e:
            print e
        defer.returnValue(cryptos)
