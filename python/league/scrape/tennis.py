from league import league_shared
from twisted.web.client import getPage
from app import fixed
from lxml import html, etree
from twisted.internet import defer

import json
from app import keys, parse
import re

class TOURNAMENTS(league_shared.Common):
    
    def clean_tennis(self, tn):
        tn = tn.replace('(tennis)', '')
        return tn.strip()

    def get_grandslams(self, itf_html):
        h2 = itf_html.cssselect('a[title="International Tennis Federation"][href="/wiki/International_Tennis_Federation"]')[0].getparent().getparent()
        print h2.tag
        while h2.tag != 'table':
            h2 = h2.getnext()
        grand_slams = []        
        for tr in h2.cssselect('tr')[1:]:
            tourney = {}
            tourney[keys.entity_profile] = fixed.clean_url('http://en.wikipedia.org' + tr[0][0].attrib['href'])
            tourney[keys.entity_name] = self.clean_tennis(tr[0][0].attrib['title'])
            tourney['schedule'] = parse.csstext(tr[1])
            tourney['town'] = parse.csstext(tr[2])
            tourney['country'] = tr[3][0].tail
            tourney['continent'] = parse.csstext(tr[4])
            tourney['surface'] = parse.csstext(tr[5])
            tourney['established'] = parse.csstext(tr[6])
            grand_slams.append(tourney)
        return grand_slams   

    def get_shared_tourney(self, h2):
        print h2.tag
        while h2.tag != 'table':
            h2 = h2.getnext()
        st = []        
        for tr in h2.cssselect('tr')[1:]:        
            tourney = {}
            tourney[keys.entity_profile] = fixed.clean_url('http://en.wikipedia.org' + tr[3][0].attrib['href'])
            tourney[keys.entity_name] = self.clean_tennis(tr[3][0].attrib['title'])
            tourney['week'] = parse.csstext(tr[0])
            tourney['starts'] = parse.csstext(tr[1])
            tourney['surface'] = parse.csstext(tr[4]).split(' ')[0]
            
            tourney['town'] = parse.csstext(tr[5])
            tourney['country'] = tr[6][0].tail
            tourney['continent'] = parse.csstext(tr[7])
            tourney[keys.entity_prizemoney] = parse.csstext(tr[8])
            st.append(tourney)
        return st       

    def get_wta(self, itf_html):  
        h2 = itf_html.cssselect('span[id="WTA_Tour"][class="mw-headline"]')[0].getparent()
        return self.get_shared_tourney(h2)
    
    def get_atp(self, itf_html):  
        h2 = itf_html.cssselect('a[title="Association of Tennis Professionals"][href="/wiki/Association_of_Tennis_Professionals"]')[0].getparent().getparent()
        return self.get_shared_tourney(h2)

    @defer.inlineCallbacks
    def entities(self):
        d = getPage('https://en.wikipedia.org/wiki/List_of_tennis_tournaments#WTA_Tour')
        d.addCallback(etree.HTML)    
        itf_html = yield d 
        gs = self.get_grandslams(itf_html)
        atp = self.get_atp(itf_html)
        wta = self.get_wta(itf_html)
        for a in atp + wta:
            if a[keys.entity_profile] not in [g[keys.entity_profile] for g in gs]:
                gs.append(a)
        defer.returnValue(gs)

class TENNIS(league_shared.SharedLeague):
    
    chrome_scraper = False
    
    rank_difference_filter = 2
    
    min_size = 990
    max_size = 1300
    
    womens_base = 'http://www.wtatennis.com'
    mens_base = 'http://www.atpworldtour.com'

    def filter_tweet(self, msg):
        if 'rank__change' in msg:
            f = int(msg['rank__change'].split('__')[0])
            t = int(msg['rank__change'].split('__')[1])
            if abs(f) < 50 or abs(t) < 50:
                return False
        print 'filtered'
        return True
     
    def womens_url(self, m):
        return TENNIS.womens_base + '/node/' + m  + '/singles/ranking.json' 
    
    mens_rankings = mens_base + '/en/rankings/singles'    
    default_entity_types = ['player','event']
    
    def men(self, body):
        doc = html.document_fromstring(body.decode("utf-8"))
        trs = doc.xpath('//div[@id="rankingDetailAjaxContainer"]/table[@class="mega-table"]/tbody/tr')
        players = []
        for tr in trs:
            player = {}
            player[keys.entity_rank] = tr[0].text.strip() 
            player[keys.entity_name] = tr.xpath('td[@class="player-cell"]/a')[0].text 
            player[keys.entity_profile] = fixed.clean_url(self.mens_base + tr.xpath('td/a')[0].attrib['href']) 
            player[keys.entity_country] = tr.xpath('td[@class="country-cell"]/div/div/img')[0].attrib['alt']
            player[keys.entity_team] = 'ATP World Tour'
            player[keys.entity_gender] = 'Male'
            players.append(player)
        return players

    @defer.inlineCallbacks
    def get_men(self):
        d = getPage(TENNIS.mens_rankings)
        d.addErrback(self.error_league)
        first_html = yield d
        players = self.men(first_html)
        for offset in ['101-200', '201-300', '301-400', '401-500']:
            uri=self.mens_rankings +'/en/rankings/singles/?countryCode=all&rankRange=' + offset
            d = getPage(uri)
            d.addErrback(self.error_league)
            html = yield d
            players.extend(self.men(html))
        defer.returnValue(players)

    def women(self, body):
        w = json.loads(body)
        players = []
        for p in [p2 for p2 in w if p2['rank'] < 501]:
            player = {}
            player[keys.entity_rank] = p['rank']
            player[keys.entity_age] = p['age']
            
            fullname = html.document_fromstring(p['fullname'])
            player[keys.entity_name] = parse.csstext(fullname.cssselect('div')[0])
            href = fullname.cssselect('a')[0].attrib['href']
            if href.startswith('/'):
                href = href[1:]
            player[keys.entity_profile] = fixed.clean_url(self.womens_base + '/' + href)
            
            country = html.document_fromstring(p['country'])
            player[keys.entity_country] = country.cssselect('span')[0].attrib['data-tooltip']
            
            player[keys.entity_team] = 'WTA Tennis'            
            player[keys.entity_gender] = 'Female'
            #print player
            #print p
            players.append(player)
        return players

    @defer.inlineCallbacks
    def get_women(self):
        rankings = yield getPage('http://www.wtatennis.com/rankings')
        rankings = rankings.replace('\/', '/')
        #http://www.wtatennis.com/node/227956/singles/ranking.json
        #print rankings
        rd = re.search('node/(.*)/singles/ranking.json', rankings).group(1)
        url = self.womens_url(rd)
        print url
        d = getPage(url)        
        d.addErrback(self.error_league)
        first_html = yield d
        players = self.women(first_html)
        #for offset in ['101','201','301','401']:
        #    url = self.womens_base + '/fragment/wtaTennis/fragments/assets/rankings/rankingsData/type/SINGLES/date/' + time.strftime('%m%d%Y') + '/pag/' + offset
        #    print url
        #    d = getPage(url)
        #    d.addErrback(self.error_league)
        #    html = yield d
        #    players.extend(self.women(html))
        print 'women players:', len(players)
        defer.returnValue(players)

    def entities(self):
        dl = defer.DeferredList([self.get_women(), self.get_men(), TOURNAMENTS().entities()])
        dl.addBoth(lambda res: res[0][1] + res[1][1] + res[2][1])
        return dl
