from league import league_shared

from twisted.internet import defer
from twisted.web.client import getPage

from app import keys, fixed, parse
from lxml import etree

class TOURNAMENTS(league_shared.Common):

    def get_events(self, html):
        tourneys = []
        p = html.cssselect('span[id="Schedule"]')[0].getparent()
        while p.tag != 'table':
            p = p.getnext()
        for tr in p.cssselect('tr'):
            try:
                date = parse.csstext(tr[0])
                profile = 'http://en.wikipedia.org' + tr[1][0].attrib['href']
                name = tr[1][0].attrib['title']
                location = parse.csstext(tr[2])
                purse = parse.csstext(tr[5])
                print date, profile, name, location, purse
                tourney = {}
                tourney[keys.entity_event_date] = date
                tourney[keys.entity_profile] = profile
                tourney[keys.entity_location] = location
                tourney[keys.entity_name] = name
                tourney[keys.entity_prizemoney] = purse
                tourneys.append(tourney)
            except Exception as e:
                print 'tourney exception:', e
        print 'tourneys:', tourneys
        return tourneys
    
    @defer.inlineCallbacks
    def entities(self):
        d = getPage('http://en.wikipedia.org/wiki/2018_PGA_Tour')
        d.addCallback(etree.HTML)    
        itf_html = yield d 
        events = self.get_events(itf_html)
        print 'events:', events
        defer.returnValue([])

class GOLF(league_shared.SharedLeague):
    
    min_size = 900
    max_size = 1200

    golf_base = 'http://www.pgatour.com'
    golf_rankings = golf_base + '/stats/stat.186.html'
    
    
    def filter_tweet(self, msg):
        if 'rank__change' in msg:
            f = int(msg['rank__change'].split('__')[0])
            t = int(msg['rank__change'].split('__')[1])
            if abs(f) < 50 or abs(t) < 50:
                return False
        print 'filtered!'
        return True

    def get_golfers(self, h):
        team = {}
        team['team'] = 'pga'
        players = []
        for tr in h.cssselect('table[id="statsTable"].table-styled tr'):
            print 'tr:', tr
            try:
                if len(tr) == 9:
                    player = {}
                    player[keys.entity_rank] = tr[0].text.strip()
                    player[keys.entity_name] = tr[2][0].text.strip().replace(u'\xa0', u' ')
                    player[keys.entity_profile] = fixed.clean_url(self.golf_base + tr[2][0].attrib['href'].replace('content/pgatour/', ''))
                    try:
                        player[keys.entity_country] = tr[8].text.strip()
                    except:
                        pass
                    players.append(player)
            except Exception as e:
                print 'golfer exception:', e                
        return players    
        
    @defer.inlineCallbacks
    def entities(self):
        print 'golf players:', self.golf_rankings
        yield self.cv.goto_url(self.golf_rankings)
        html = yield self.cv.to_html()
        golfers = self.get_golfers(html)
        tourneys = yield TOURNAMENTS().entities()
        yield defer.returnValue(golfers + tourneys)        
