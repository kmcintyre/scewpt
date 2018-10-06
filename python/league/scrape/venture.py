from league import league_shared
from twisted.internet import reactor, defer, task
from app import keys, fixed, parse
from urlparse import urlparse

import json

js_link="""
document.querySelectorAll('table[id="data-table"] tbody tr')[%s].click()
"""
components = []
with open('/home/ubuntu/scewpt/etc/data/venture/wsj_billion_dollar.json') as json_data:
    wbd = json.load(json_data)

print 'adjustment size:', len(wbd)
    
class WSJ_BILLION_DOLLAR(league_shared.Common):

    @defer.inlineCallbacks
    def getComponents(self):
        components = []
        yield self.cv.goto_url('http://graphics.wsj.com/billion-dollar-club/').addCallback(lambda ign: task.deferLater(reactor, 5, defer.succeed, True))
        html = yield self.cv.to_html()        
        for i, company in enumerate(html.cssselect('table[id="data-table"] tbody tr')):
            player = { keys.entity_team: 'WSJ Billion Dollar Startup'}
            player[keys.entity_rank] = i + 1
            player[keys.entity_name] = parse.csstext(company.cssselect('td.company')[0]).strip()
            player[keys.entity_valuation] = parse.csstext(company.cssselect('td.valuation')[0])
            player[keys.entity_total_funding] = parse.csstext(company.cssselect('td.total_funding')[0])
            player[keys.entity_last_valuation] = parse.csstext(company.cssselect('td.val_date')[0])

            self.cv.page().runJavaScript(js_link % str(i))
            
            d = task.deferLater(reactor, 1, defer.succeed, True)
            d.addCallback(self.cv.to_html)
            html2 = yield d
            dets = html2.cssselect('tr.card-tr')[0]            
            try:
                player[keys.entity_rounds] = parse.csstext(dets.cssselect('div[class="rounds co-info"]')[0][1])
            except:
                pass
            for ceo in dets.cssselect('div[class="ceo co-info"]'):
                ceo_txt = parse.csstext(ceo).replace('CEO:','')
                c = ceo_txt.split('(co-founder)')[0].split('(founder)')[0].split(', founder')[0].split(', founder')[0].split('(co-founders)')[0].split(', co-founder')                          
                for rceo in c[0].split(' and '):
                    rceo = rceo.strip()
                    if keys.entity_ceo not in player:
                        player[keys.entity_ceo] = [rceo]
                    else:
                        player[keys.entity_ceo].append(rceo)                            
            player[keys.entity_ratio] = parse.csstext(dets.cssselect('div[class="ratio co-info"] span[class="val"]')[0])
            player[keys.entity_location] = parse.csstext(dets.cssselect('div[class="location co-info"] span[class="val"]')[0])
            player[keys.entity_competitors] = parse.csstext(dets.cssselect('p[class="competitors co-info"] span[class="val"]')[0])
            player[keys.entity_investors] = parse.csstext(dets.cssselect('p[class="investors co-info"] span[class="val"]')[0])
            components.append(player)        
        defer.returnValue(components)                
    
    @defer.inlineCallbacks
    def adjustments(self, components):
        print 'adjustments components len:', len(components)
        for c in components:
            cites = yield self.cv.bing(c[keys.entity_name])
            if cites[0]:
                from urlparse import urlparse                
                c[keys.entity_profile] = fixed.clean_url('http://' + urlparse(fixed.simpleurl(cites[0])).netloc)
                print c[keys.entity_name], 'bing profile:', c[keys.entity_profile]
                for key in wbd:                
                    if key[0] == c[keys.entity_name] and c[keys.entity_profile] != key[1]:
                        c[keys.entity_profile] = key[1]
                        print '        ', c[keys.entity_profile]
                print 'profile:', c[keys.entity_profile], c[keys.entity_name]            
        defer.returnValue([c for c in components if keys.entity_profile in c])
    
    @defer.inlineCallbacks
    def entities(self):                        
        d = self.getComponents()        
        d.addCallback(self.adjustments)        
        d.addErrback(self.error_league)
        ans = yield d
        defer.returnValue(ans)

class VC100(league_shared.Common):
    
    def entrepreneurVC100(self, html):
        components = []             
        for h2s in html.cssselect('h2[class="slides"]'):
            player = { keys.entity_team: 'Entrepreneur VC 100' }
            player[keys.entity_rank] = parse.csstext(h2s).split(' ')[0][1:]
            player[keys.entity_name] = h2s.find('./a').text
            player[keys.entity_location] = h2s.find('./a').tail[1:]
            player[keys.entity_profile] = fixed.clean_url('http://' + urlparse(h2s.cssselect('a')[0].attrib['href']).netloc)
            if len(player[keys.entity_profile]) > 7:
                player[keys.entity_location] = parse.csstext(h2s).split(',', 1)[1].strip()
                if h2s.getnext()[0].tag.lower() == 'img':
                    player[keys.entity_pic] = h2s.getnext().cssselect('img')[0].attrib['src']
                    player[keys.entity_investments] = parse.csstext(h2s.getnext().getnext()).split(' ')[-1] + 'M'                    
                    try:
                        player[keys.entity_deals] = parse.csstext(h2s.getnext().getnext().getnext())                            
                    except:
                        pass
                else:
                    player[keys.entity_investments] = parse.csstext(h2s.getnext()).split(' ')[-1] + 'M'
                    player[keys.entity_deals] = parse.csstext(h2s.getnext().getnext()).split(' ')[-1]
            components.append(player)
        return components

    def entities(self):
        d = self.cv.goto_url('http://www.entrepreneur.com/article/242702')
        d.addCallback(self.cv.to_html)
        d.addCallback(self.entrepreneurVC100)
        d.addErrback(self.error_league)
        return d

class THEFUNDED(league_shared.Common):
    
    def thefundedTopRatedVCs(self, html):
        components = []
        for rank in html.cssselect('div[id="post"]')[0].cssselect('p[class="larger red"]'):
            player = { keys.entity_team: 'TheFunded Top Partners' }
            player[keys.entity_rank] = parse.csstext(rank)[:-1]
            player[keys.entity_name] = parse.csstext(rank.getnext().cssselect('a')[0])
            player[keys.entity_profile] = fixed.clean_url('http://www.thefunded.com' + rank.getnext().cssselect('a')[0].attrib['href'])
            player[keys.entity_firm] = parse.csstext(rank.getparent().cssselect('a[class="fund"]')[0])
            print 'player:', player            
            components.append(player)
        return components

    def entities(self):
        d = self.cv.goto_url('http://www.thefunded.com/funds/top_partners')
        d.addCallback(self.cv.to_html)
        d.addCallback(self.thefundedTopRatedVCs)        
        d.addErrback(self.error_league)
        return d
        
class MICROVC(league_shared.Common):

    def firms(self):
        firms = []
        with open('/home/ubuntu/scewpt/etc/data/venture/venture_firms.txt') as f:            
            for line in f:
                firm = { keys.entity_team: 'Micro VC'}
                firm_seq = eval(line)
                firm[keys.entity_name] = firm_seq[0]
                firm[keys.entity_origin] = firm_seq[1]
                firm[keys.entity_sector] = firm_seq[2]
                
                firms.append(firm)
        return firms

    @defer.inlineCallbacks
    def entities(self):
        firms = self.firms()
        for firm in firms:
            d = self.cv.bing(firm[keys.entity_name])
            d.addErrback(self.error_league)
            cites = yield d            
            if cites:
                firm[keys.entity_profile] = fixed.clean_url(cites[0])
        defer.returnValue([f for f in firms if keys.entity_profile in f])            

class BILLION_DOLLAR_CEO(league_shared.Common):

    def is_born(self, html):    
        for th in html.cssselect('th'):
            if parse.csstext(th).lower() in ['born', 'date of birth']:
                return True
        return False
    
    @defer.inlineCallbacks
    def createCeoTeam(self, components):
        ceos = []        
        for player in components:
            if keys.entity_ceo in player:
                for ceo in player[keys.entity_ceo]:
                    ceo_player = { keys.entity_team: 'Billion Dollar CEO'}
                    ceo_player[keys.entity_company] = player[keys.entity_name]
                    ceo_player.update({ keys.entity_name: ceo })
                    print 'lookup:', ceo                    
                    d = self.cv.google(ceo, domain='en.wikipedia.org')
                    d.addErrback(self.error_league)
                    res = yield d
                    if res and res[0]:
                        print 'wikipedia to profile:',  res[0]                    
                        ceo_player[keys.entity_profile] = fixed.clean_url(res[0])
                        isb = yield self.cv.goto_url(ceo_player[keys.entity_profile]).addCallback(lambda ign: self.cv.to_html()).addCallback(self.is_born)
                        if isb:
                            ceos.append(ceo_player)
            else:
                print 'NO ceo!', player[keys.entity_name]
        defer.returnValue(ceos)     

    def entities(self, components):
        d = self.createCeoTeam(components)
        d.addErrback(self.error_league)
        return d

class VENTURE(league_shared.SharedLeague):
    
    min_size = 600
    max_size = 800
    
    @defer.inlineCallbacks    
    def entities(self):
        venture = []
        w = WSJ_BILLION_DOLLAR()
        w.cv = self.cv
        wsj = yield w.entities()
        print 'wall street journal billion dollar:', len(wsj)
        venture.extend(wsj)
        
        v = VC100()
        v.cv = self.cv
        vc100 = yield v.entities()
        print 'vc100:', len(vc100)
        venture.extend(vc100)
        
        t = THEFUNDED()
        t.cv = self.cv
        thefunded = yield t.entities()
        print 'the funded:', len(thefunded)
        venture.extend(thefunded)

        m = MICROVC()
        m.cv = self.cv
        microvc = yield m.entities()
        print 'micro vc:', len(microvc)
        venture.extend(microvc)
        
        bdc = yield BILLION_DOLLAR_CEO().entities(wsj)
        print 'billion dollar ceo:', len(bdc)
        venture.extend(bdc)
        
        defer.returnValue(venture)