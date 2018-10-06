from league import league_shared
from app import fixed, keys, parse

from twisted.internet import defer
import re

class FBS(league_shared.TeamSportsLeague):
    
    min_size = 500
    max_size = 2000
    
    def get_players_inline(self, html, team):
        print 'get players'
        t = html.cssselect('figure.Logo.Nav__Secondary__Menu__Logo')[0]
        tn = parse.csstext(t.getnext())
        print 'team name:', tn
        team['team'] = tn
        print 'team:',  team['team']
        team['players'] = []
        for tr in html.cssselect('tr[data-idx].Table2__tr')[2:]:
            player = {}
            tds = tr.cssselect('td')
            player[keys.entity_jersey] = parse.csstext(tds[0])
            player[keys.entity_name] = parse.csstext(tds[1].cssselect('a')[0])
            player[keys.entity_profile] = fixed.clean_url(tds[1].cssselect('a')[0].attrib['href'])
            player[keys.entity_position] = parse.csstext(tds[2])
            player[keys.entity_height] = parse.csstext(tds[3])
            player[keys.entity_height] = re.sub('[^0-9_-]+', '', player[keys.entity_height].replace(' ','-'))
            player[keys.entity_weight] = parse.csstext(tds[4]).split(' ')[0]
            player[keys.entity_class] = parse.csstext(tds[5])
            player[keys.entity_origin] = parse.csstext(tds[6])
            team['players'].append(player)            
        print 'college done:', team['team'], len(team['players'])
    
    @defer.inlineCallbacks
    def get_players(self, html, team):
        while 'players' not in team:
            try:
                self.get_players_inline(html, team)
                defer.returnValue(team)
            except Exception as e:
                print 'retry', e
                html = yield self.cv.goto_url(self.cv.page().url().toString()).addCallback(self.cv.to_html)            

    @defer.inlineCallbacks
    def get_rosters(self, teams):
        for team in teams:
            print 'get_rosters:', team, team['roster_link']
            html = yield self.cv.goto_url(team['roster_link']).addCallback(self.cv.to_html)
            self.get_players(html, team)
        print 'get rosters done'
        defer.returnValue(teams)

    def get_teams(self, html):
            teams = []
            for conference in html.cssselect('div.mt7'):
                conference_name = parse.csstext(conference.cssselect('div.headline')[0])
                conference_name = conference_name.lower().replace(' ', '').replace('-','').replace('americanathletic', 'aac').replace('midamerican', 'mac').replace('conferenceusa', 'cusa').replace('fbsindependents', 'fbsindependent')
                if conference_name == self.get_league_name():
                    print 'conference:', conference_name, len(conference.cssselect('section.TeamLinks'))
                    for section in conference.cssselect('section.TeamLinks'):                        
                        team = { 'conference': conference_name, 'link': 'http://espn.go.com' + section.cssselect('a')[0].attrib['href']}
                        for a in section.cssselect('div.TeamLinks__Links span.TeamLinks__Link a'):
                            if parse.csstext(a).lower() == 'roster':
                                roster_link = 'http://espn.go.com' + a.attrib['href']
                                team['roster_link'] = roster_link 
                        teams.append(team)
            print teams
            return teams

    def conference(self):
        pass

    def entities(self):
        d = self.cv.goto_url('http://espn.go.com/college-football/teams')
        d.addCallback(self.cv.to_html)
        d.addCallback(self.get_teams)
        d.addCallback(self.get_rosters)
        d.addCallback(self.teams_to_players)
        d.addErrback(self.error_league)
        return d