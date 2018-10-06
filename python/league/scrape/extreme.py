from league import league_shared
from twisted.internet import defer
from app import keys, fixed, parse

import requests

class SURF(league_shared.Common):
    
    surfing = 'Surf'

    def get_community(self, html, community, gender='Male'):
        trs = html.cssselect('table[class="tableType-athlete hasGroups"]')[0].cssselect('tr')
        print 'community length:', len(trs)
        for tr in trs:
            player = {}
            try:
                                
                player[keys.entity_rank] = parse.csstext(tr.cssselect('td[class~="athlete-tour-rank"]')[0])
                #player[keys.entity_rank_change] = parse.csstext(tr.cssselect('td[class="athlete-tour-rank-change"]')[0])
                name_element = parse.csstext(tr.cssselect('a[class="athlete-name"]')[0]).title()
                player[keys.entity_name] = name_element.replace('INJU','').replace('RECO','').strip()
                player[keys.entity_profile] = fixed.clean_url('http://www.worldsurfleague.com' + tr.cssselect('a[class="athlete-name"]')[0].attrib['href'])
                player[keys.entity_origin] = tr.cssselect('span.athlete-country-flag')[0].attrib['title']
                player[keys.entity_points] = parse.csstext(tr.cssselect('span[class="tour-points"]')[0])
                player[keys.entity_prizemoney] = parse.csstext(tr.cssselect('td[class~="athlete-tour-prize-money"]')[0])
                if player[keys.entity_name]:
                    player[keys.entity_team] = self.surfing                    
                    community.append(player)
            except Exception as e:
                if keys.entity_name in player:
                    player[keys.entity_team] = self.surfing                    
                    community.append(player)                
    
    @defer.inlineCallbacks
    def mct(self):
        community = []
        mct_url = 'http://www.worldsurfleague.com/athletes/tour/mct'
        print 'mct url:', mct_url
        html = yield self.cv.goto_url(mct_url).addBoth(self.cv.to_html)
        self.get_community(html, community)
        next_anchor = html.cssselect('li.next a')
        while len(next_anchor) > 0:
            next_href = 'http://www.worldsurfleague.com' + next_anchor[0].attrib['href']
            html = yield self.cv.goto_url(next_href).addCallback(self.cv.to_html)
            self.get_community(html, community)
            next_anchor = html.cssselect('li.next a')          
        defer.returnValue(community)

    @defer.inlineCallbacks
    def mqs(self):
        community = []
        mqs_url = 'http://www.worldsurfleague.com/athletes/tour/mqs'
        print 'mqs url:', mqs_url
        html = yield self.cv.goto_url(mqs_url).addBoth(self.cv.to_html)
        self.get_community(html, community)
        next_anchor = html.cssselect('li.next a')
        while len(next_anchor) > 0 and 'offset=301' not in next_anchor[0].attrib['href']:
            next_href = 'http://www.worldsurfleague.com' + next_anchor[0].attrib['href']
            html = yield self.cv.goto_url(next_href).addCallback(self.cv.to_html)
            self.get_community(html, community)
            next_anchor = html.cssselect('li.next a')          
        defer.returnValue(community)        

    @defer.inlineCallbacks
    def wct(self):
        community = []
        wct_url = 'http://www.worldsurfleague.com/athletes/tour/wct'
        print 'wct url:', wct_url
        html = yield self.cv.goto_url(wct_url).addBoth(self.cv.to_html)
        self.get_community(html, community, 'Female')
        next_anchor = html.cssselect('li.next a')
        while len(next_anchor) > 0:
            next_href = 'http://www.worldsurfleague.com' + next_anchor[0].attrib['href']
            html = yield self.cv.goto_url(next_href).addCallback(self.cv.to_html)
            self.get_community(html, community, 'Female')
            next_anchor = html.cssselect('li.next a')          
        defer.returnValue(community)        

    @defer.inlineCallbacks
    def wqs(self):
        community = []
        wqs_url = 'http://www.worldsurfleague.com/athletes/tour/wqs'
        print 'wqs url:', wqs_url 
        html = yield self.cv.goto_url(wqs_url).addBoth(self.cv.to_html)
        self.get_community(html, community, 'Female')
        next_anchor = html.cssselect('li.next a')
        while len(next_anchor) > 0 and 'offset=151' not in next_anchor[0].attrib['href']:
            next_href = 'http://www.worldsurfleague.com' + next_anchor[0].attrib['href']
            html = yield self.cv.goto_url(next_href).addCallback(self.cv.to_html)
            self.get_community(html, community, 'Female')
            next_anchor = html.cssselect('li.next a')          
        defer.returnValue(community)        

    @defer.inlineCallbacks
    def entities(self):
        community = []
        
        mt = yield self.mct()
        community.extend([m for m in mt if m[keys.entity_profile] not in [p[keys.entity_profile] for p in community]])
        mq = yield self.mqs()
        community.extend([m for m in mq if m[keys.entity_profile] not in [p[keys.entity_profile] for p in community]])
        
        wt = yield self.wct()
        community.extend([w for w in wt if w[keys.entity_profile] not in [p[keys.entity_profile] for p in community]])        
        wq = yield self.wqs()
        community.extend([w for w in wq if w[keys.entity_profile] not in [p[keys.entity_profile] for p in community]])

        surfing_team = {}
        surfing_team[keys.entity_profile] = 'team:' + self.surfing
        community.append(surfing_team)
        defer.returnValue(community)
        

class SNOW(league_shared.Common):
    
    snow_rankings = 'http://www.worldsnowboardtour.com'
    
    snowboarding = 'Snowboarding'
    
    ss = 'Slope Style'
    hp = 'Half Pipe'
    ba = 'Big Air'

    def get_snow(self, html, community, gender, style):
        print 'get_snow:', self.snowboarding
        for tr in html.cssselect('tr.ranking'):
            try:
                player = {}
                player[keys.entity_gender] = gender
                
                player[keys.entity_style] = style            
                player[keys.entity_rank] = parse.csstext(tr.cssselect('td span')[0]).replace('.','')
                #player[keys.entity_rank_change] = parse.csstext(tr.cssselect('td')[2])
                #player[keys.entity_rank_change] = player[keys.entity_rank_change].replace('--','-')
                player[keys.entity_name] = parse.csstext(tr.cssselect('td')[3])
                player[keys.entity_profile] = fixed.clean_url(self.snow_rankings + tr.cssselect('td')[3].cssselect('a')[0].attrib['href'].strip().split('?')[0])
                player[keys.entity_origin] = parse.csstext(tr.cssselect('td')[4])
                player[keys.entity_age] = parse.csstext(tr.cssselect('td')[5])
                player[keys.entity_sponsors] = parse.csstext(tr.cssselect('td')[6])
                player[keys.entity_points] = parse.csstext(tr.cssselect('td')[8])
                if keys.entity_profile in player.keys():    
                    player[keys.entity_team] = self.snowboarding
                    community.append(player)
            except:
                pass
                
    @defer.inlineCallbacks
    def get_community(self):
        community = []
        gender='Male'
        style = self.ss 
        yield self.cv.goto_url(self.snow_rankings + '/points-lists/?type=SS&gender=M').addCallback(self.cv.to_html).addCallback(self.get_snow, community, gender, style)
        yield self.cv.goto_url(self.snow_rankings + '/points-lists/2/?type=SS&gender=M').addCallback(self.cv.to_html).addCallback(self.get_snow, community, gender, style)
        style = self.hp
        yield self.cv.goto_url(self.snow_rankings + '/points-lists/?type=HP&gender=M').addCallback(self.cv.to_html).addCallback(self.get_snow, community, gender, style)
        yield self.cv.goto_url(self.snow_rankings + '/points-lists/2/?type=HP&gender=M').addCallback(self.cv.to_html).addCallback(self.get_snow, community, gender, style)
        style = self.ba
        yield self.cv.goto_url(self.snow_rankings + '/points-lists/?type=BA&gender=M').addCallback(self.cv.to_html).addCallback(self.get_snow, community, gender, style)
        yield self.cv.goto_url(self.snow_rankings + '/points-lists/2/?type=BA&gender=M').addCallback(self.cv.to_html).addCallback(self.get_snow, community, gender, style)

        print 'male complete'

        gender='Female'
        style = self.ss 
        yield self.cv.goto_url(self.snow_rankings + '/points-lists/?type=SS&gender=W').addCallback(self.cv.to_html).addCallback(self.get_snow, community, gender, style)
        yield self.cv.goto_url(self.snow_rankings + '/points-lists/2/?type=SS&gender=W').addCallback(self.cv.to_html).addCallback(self.get_snow, community, gender, style)
        style = self.hp
        yield self.cv.goto_url(self.snow_rankings + '/points-lists/?type=HP&gender=W').addCallback(self.cv.to_html).addCallback(self.get_snow, community, gender, style)
        yield self.cv.goto_url(self.snow_rankings + '/points-lists/2/?type=HP&gender=W').addCallback(self.cv.to_html).addCallback(self.get_snow, community, gender, style)
        style = self.ba
        yield self.cv.goto_url(self.snow_rankings + '/points-lists/?type=BA&gender=W').addCallback(self.cv.to_html).addCallback(self.get_snow, community, gender, style)
        yield self.cv.goto_url(self.snow_rankings + '/points-lists/2/?type=BA&gender=W').addCallback(self.cv.to_html).addCallback(self.get_snow, community, gender, style)
        
        print 'snow length:', len(community)
        snowboard_team = {}
        snowboard_team[keys.entity_profile] = 'team:' + self.snowboarding
        community.append(snowboard_team)
        defer.returnValue(community)

    def entities(self):        
        d = self.get_community()
        d.addErrback(self.error_league)
        return d

class SKATE(league_shared.Common):
    
    profile_remove_list = ['div#InterstitialContainer']    
    skating = 'Skate'

    def get_skater(self, html, community):
        for tr in html.cssselect('table.vitals.vitalsshrink tr')[1:]:
            skater = {}
            skater[keys.entity_rank] = parse.csstext(tr[0])[:-2]
            skater[keys.entity_profile] = fixed.clean_url(tr[1].cssselect('a')[0].attrib['href'])
            skater[keys.entity_name] = parse.csstext(tr[2].cssselect('a')[0]).replace(',','')
            skater[keys.entity_country] = parse.csstext(tr[2].cssselect('a')[1])
            try:
                skater[keys.entity_age] = tr.cssselect('h3 br')[0].tail.strip().split(' ')[1]
                skater[keys.entity_points] = tr.cssselect('h3 br')[1].tail.strip().split(' ')[1]
            except:
                try:
                    skater[keys.entity_points] = tr.cssselect('h3 br')[0].tail.strip().split(' ')[1]
                except:
                    pass
            pic_url = 'https://theboardr.blob.core.windows.net/headshots/' + skater[keys.entity_profile].split('/')[4] + '_900.jpg'
            check = requests.head(pic_url, headers={'User-Agent': 'curl/7.35.0', 'Accept': '*/*'}, verify=True)
            if check.status_code == 200:
                skater[keys.entity_pic] = pic_url
            skater[keys.entity_team] = self.skating
            community.append(skater) 
            
    @defer.inlineCallbacks
    def get_community(self):
        community=[]        
        yield self.cv.goto_url('https://theboardr.com/globalrank').addCallback(self.cv.to_html).addCallback(self.get_skater, community)
        print 'page1 complete:', len(community)
        yield self.cv.goto_url('https://theboardr.com/globalranktest?&Page=2').addCallback(self.cv.to_html).addCallback(self.get_skater, community)
        print 'page2 complete:', len(community)
        yield self.cv.goto_url('https://theboardr.com/globalranktest?&Page=3').addCallback(self.cv.to_html).addCallback(self.get_skater, community)
        print 'page3 complete:', len(community)        
        yield self.cv.goto_url('https://theboardr.com/globalranktest?&Page=4').addCallback(self.cv.to_html).addCallback(self.get_skater, community)
        print 'page4 complete:', len(community)
        yield self.cv.goto_url('https://theboardr.com/globalranktest?&Page=5').addCallback(self.cv.to_html).addCallback(self.get_skater, community)
        print 'skater length:', len(community)
        skater_team = {}
        skater_team[keys.entity_profile] = 'team:' + self.skating        
        community.append(skater_team)
        defer.returnValue(community)

    def entities(self):        
        d = self.get_community()
        d.addErrback(self.error_league)
        return d

class CYCLE(league_shared.Common):
    
    @defer.inlineCallbacks
    def get_community(self, html, community):
        subteams = {}
        for cycling_team in html.cssselect('.team_box')[0].cssselect('ul li'):
            jersey_pic = cycling_team.cssselect('a img')[0].attrib['src']            
            thref = 'http://www.cyclingnews.com' + cycling_team.cssselect('a')[0].attrib['href']
            print 'team url:', thref 
            subteam = {}
            subteam[keys.entity_jersey_pic] = jersey_pic             
            subteams[thref] = subteam
        for k, st in subteams.iteritems():            
            d = self.cv.goto_url(k)
            d.addCallback(self.cv.to_html)
            d.addErrback(self.error_league)
            subhtml = yield d
            team_name = parse.csstext(subhtml.cssselect('div[class="team-name"]')[0])
            st[keys.entity_profile] = 'team:' + team_name
            print 'cycle team:', st
            
            for rider in subhtml.cssselect('div.riders div.rider'):
                player = {}
                player[keys.entity_team] = team_name
                player[keys.entity_name] = parse.csstext(rider.cssselect('a')[0])
                player[keys.entity_profile] = fixed.clean_url('http://www.cyclingnews.com' + rider.cssselect('a')[0].attrib['href'])
                #print 'found one!:', player
                community.append(player)
        for p in community:
            d = self.cv.goto_url(p[keys.entity_profile] + "/")
            d.addCallback(self.cv.to_html)
            d.addErrback(self.error_league)
            riderhtml = yield d
            try:
                rider = riderhtml.cssselect('rider-info-boxout')[0]
                p[keys.entity_pic] = rider.cssselect('img.rider-image')[0].attrib['src']
                p[keys.entity_dob] = parse.csstext(rider.cssselect('span[itemprop="birthDate')[0])
                p[keys.entity_nationality] = parse.csstext(rider.cssselect('span[itemprop="nationality')[0])
            except:
                pass
        community.extend(subteams.values())
        defer.returnValue(community)

    def entities(self):
        community=[]
        d = self.cv.goto_url('http://www.cyclingnews.com/teams')
        d.addCallback(self.cv.to_html)
        d.addCallback(self.get_community, community)
        d.addErrback(self.error_league)
        return d

class EXTREME(league_shared.SharedLeague):    

    rank_difference_filter = 2

    min_size = 1600
    max_size = 2300
    
    def filter_tweet(self, msg):
        print 'filtered'
        return True
    
    def filter_tweet2(self, msg):
        if 'rank__change' in msg:
            a = int(msg['rank__change'].split('__')[0])
            b = int(msg['rank__change'].split('__')[1])
            c = max(a, b)
            d = min(a, b)
            pd = c - d
            print 'rank difference:', pd
            if pd < 6:
                print 'not enough rank difference!'
                return True
        return False 
    
    @defer.inlineCallbacks    
    def entities(self):
        from PyQt5.QtWebEngineWidgets import QWebEngineSettings
        riders = []

        s = SNOW()
        s.cv = self.cv
        snow = yield s.entities()        
        print 'snow:', len(snow)
        riders.extend(snow)
        
        c = CYCLE()
        c.cv = self.cv
        self.cv.page().settings().setAttribute(QWebEngineSettings.JavascriptEnabled, False)
        cycle = yield c.entities()
        print 'cycle:', len(cycle)
        riders.extend(cycle)
        
        self.cv.page().settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        sk = SKATE()
        sk.cv = self.cv
        skate = yield sk.entities()
        print 'skate:', len(skate)
        riders.extend(skate)

        su = SURF()
        su.cv = self.cv
        surf = yield su.entities()
        print 'surf:', len(surf)
        riders.extend(surf)
        
        defer.returnValue(riders)