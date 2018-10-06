from league import league_shared
from app import keys, fixed

from twisted.web.client import getPage
from twisted.internet import defer

from lxml import html

class FELONS(league_shared.Common):
    
    @defer.inlineCallbacks
    def proccess_pages(self, window):
        yield window.goto_url('http://www.sandiegouniontribune.com/nfl/arrests-database/')
        
    @defer.inlineCallbacks
    def entities(self):
        defer.returnValue([])

class NFL(league_shared.TeamSportsLeague):
    
    chrome_scraper = False
    
    def decorate_player_svg(self, player, tweet):
        return self.strong(player[keys.entity_position])
    
    profile_remove_list = ['div#page-top-ad','div.bp-modal-takeover']

    nfl_url = 'http://www.nfl.com'
    team_limit = 0
    team_player_limit = 0

    def error_nfl(self, err):
        print 'nfl error:', err
                
    def key_lookup(self, key):
        if key == 'high school':
            return keys.entity_high_school
        elif key == 'sck':
            return keys.entity_sacks
        elif key == 'in 20':
            return keys.entity_inside_20
        elif key == 'ff':
            return keys.entity_forced_fumbles
        elif key == 'tckl':
            return keys.entity_tackles
        elif key == 'int':
            return keys.entity_interceptions
        elif key == 'fgm':
            return keys.entity_field_goals_made
        elif key == 'fga':
            return keys.entity_field_goals_attempted
        elif key == 'rec':
            return keys.entity_receptions
        elif key == 'tds':
            return keys.entity_touchdowns
        elif key == 'avg':
            return keys.entity_average
        elif key == 'lng':
            return keys.entity_long        
        elif key == 'yds':
            return keys.entity_yards
        elif key == 'car':
            return keys.entity_carries        
        elif key == 'pct':
            return keys.entity_percentage
        elif key == 'g':
            return keys.entity_games
        elif key == 'gs':
            return keys.entity_games_started                 
        elif key == 'rtg':
            return keys.entity_rating                 
        return key

    def extended_profile(self, body, p):
        doc = html.document_fromstring(body)
        n = doc.xpath('//div[@id="player-bio"]')[0]
        pic = n.xpath('//div[@class="player-photo"]/img/@src')[0]
        p[keys.entity_pic] = pic
        strong = n.xpath('//div[@class="player-info"]/p/strong')
        for s in strong:
            if len(s.tail[2:].strip()) > 0:
                key = self.key_lookup(s.text.lower())
                #print 'key:', key, s.tail[2:].strip()
                p[key] = s.tail[2:].strip()
        for qs in doc.xpath('//p[@class="player-quick-stat-item-header"]'):
            key = self.key_lookup(qs.text.lower())
            #print 'key:', key, qs.getnext().text
            p[key] = qs.getnext().text

    def extract_players(self, doc, team):
        try:
            n = doc.xpath('//div[@id="searchResultsLargeTable"]//tbody[1]')[0]
            for a in n:
                player_data = {}
                player_data[keys.entity_name] = a[2][0].text
                player_data[keys.entity_profile] = fixed.clean_url('http://www.nfl.com' + a[2][0].attrib['href'])
                player_data[keys.entity_position] = a[0].text
                player_data[keys.entity_status] = a[3].text
                try:
                    if a[1].text:
                        player_data[keys.entity_jersey] = a[1].text
                except Exception as e:
                    print 'player exception:', e, team['team'] 
                team['players'].append(player_data)
        except Exception as e2:
            print 'team exception:', e2, team['team'] 
    
    @defer.inlineCallbacks
    def process_players(self, team):
        for player in team['players']: 
            d3 = getPage(player[keys.entity_profile])
            d3.addCallback(self.extended_profile, player)
            d3.addErrback(self.error_league)
            yield d3
        
    @defer.inlineCallbacks
    def process_teams(self, teams):
        for team in teams:
            print 'team:', team['roster']
            d = getPage(str(team['roster']))
            body = yield d
            doc = html.document_fromstring(body)
            self.extract_players(doc, team)
            if doc.xpath('//a[@title="Go to page 2"]'):                 
                link = doc.xpath('//a[@title="Go to page 2"]')[0].attrib['href']
                print '-page 2', 'http://www.nfl.com' + link                
                d2 = getPage('http://www.nfl.com' + link)
                body2 = yield d2            
                doc2 = html.document_fromstring(body2)
                self.extract_players(doc2, team)
            print team['team'], len(team['players'])
            yield self.process_players(team)
        defer.returnValue(teams)

    def get_teams(self, body):
        doc = html.document_fromstring(body)
        teams = []
        n = doc.xpath('//div[@id="searchResultsLargeTable"]//a')
        for a in n:
            if len(teams) < self.team_limit or self.team_limit < 1:
                teams.append({'roster': self.nfl_url + a.attrib['href'], 'team': a.text, 'division': a.getparent().getparent().find('p').find('span').text, 'players': []})
        return teams

    def entities(self):
        d = getPage('http://www.nfl.com/players/search?category=team&playerType=current')
        d.addCallback(self.get_teams)
        d.addCallback(self.process_teams)
        d.addCallback(self.teams_to_players)
        d.addErrback(self.error_league)
        return d