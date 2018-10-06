#!/usr/bin/env python
# -*- coding: utf-8 -*-
from league import league_shared

from twisted.internet import reactor, defer
from lxml import html

from app import fixed, keys, parse
class NHL(league_shared.TeamSportsLeague):
    
    seed = [
            {'link': u'http://www.nhl.com/canadiens', 'team': u'Montr\xe9al Canadiens'},
            {'link': u'http://ducks.nhl.com', 'team': u'Anaheim Ducks'}, {'link': u'http://coyotes.nhl.com', 'team': u'Arizona Coyotes'}, 
            {'link': u'http://bruins.nhl.com', 'team': u'Boston Bruins'}, {'link': u'http://sabres.nhl.com', 'team': u'Buffalo Sabres'}, 
            {'link': u'http://flames.nhl.com', 'team': u'Calgary Flames'}, {'link': u'http://hurricanes.nhl.com', 'team': u'Carolina Hurricanes'}, 
            {'link': u'http://blackhawks.nhl.com', 'team': u'Chicago Blackhawks'}, {'link': u'http://avalanche.nhl.com', 'team': u'Colorado Avalanche'}, 
            {'link': u'http://bluejackets.nhl.com', 'team': u'Columbus Blue Jackets'}, {'link': u'http://stars.nhl.com', 'team': u'Dallas Stars'}, 
            {'link': u'http://redwings.nhl.com', 'team': u'Detroit Red Wings'}, {'link': u'http://oilers.nhl.com', 'team': u'Edmonton Oilers'}, 
            {'link': u'http://panthers.nhl.com', 'team': u'Florida Panthers'}, {'link': u'http://kings.nhl.com', 'team': u'Los Angeles Kings'}, 
            {'link': u'http://wild.nhl.com', 'team': u'Minnesota Wild'}, 
            {'link': u'http://predators.nhl.com', 'team': u'Nashville Predators'}, {'link': u'http://devils.nhl.com', 'team': u'New Jersey Devils'}, 
            {'link': u'http://islanders.nhl.com', 'team': u'New York Islanders'}, {'link': u'http://rangers.nhl.com', 'team': u'New York Rangers'}, 
            {'link': u'http://senators.nhl.com', 'team': u'Ottawa Senators'}, {'link': u'http://flyers.nhl.com', 'team': u'Philadelphia Flyers'}, 
            {'link': u'http://penguins.nhl.com', 'team': u'Pittsburgh Penguins'}, {'link': u'http://sharks.nhl.com', 'team': u'San Jose Sharks'}, 
            {'link': u'http://blues.nhl.com', 'team': u'St. Louis Blues'}, {'link': u'http://lightning.nhl.com', 'team': u'Tampa Bay Lightning'}, 
            {'link': u'http://mapleleafs.nhl.com', 'team': u'Toronto Maple Leafs'}, {'link': u'http://canucks.nhl.com', 'team': u'Vancouver Canucks'}, 
            {'link': u'http://capitals.nhl.com', 'team': u'Washington Capitals'}, {'link': u'http://jets.nhl.com', 'team': u'Winnipeg Jets'}]

    nhl_url = 'http://www.nhl.com'

    def process_players(self, html, team):
        team['players'] = []
        positions = ['Forwards', 'Defense', 'Goalies', 'Attaquants', 'Défenseurs', 'Gardiens']
        for divtables in html.cssselect('table.split-table'):
            h3 = divtables.getprevious()            
            if parse.csstext(h3) in positions:
                position = parse.csstext(h3)
                print position
                if positions.index(position) > 2:
                    position = positions[positions.index(position)-3]
                if position[-1] == 's':
                    position = position[:-1]
                ptable = divtables[0].cssselect('table')[0]
                stable = divtables[0].cssselect('table')[1]
                for i, tr in enumerate(ptable.cssselect('tr')[1:]):
                    player = {}
                    path = tr.cssselect('td.name-col a')[0].attrib['href']
                    if path.startswith('/fr/'):
                        path = path[3:]
                    try:
                        player[keys.entity_profile] = fixed.clean_url('http://www.nhl.com' + path)
                        player[keys.entity_pic] = tr.cssselect('td.name-col a img.player-photo')[0].attrib['src']
                        spans = tr.cssselect('td.name-col a div span')
                        player[keys.entity_name] = ' '.join([parse.csstext(spans[1]), parse.csstext(spans[2])])                    
                        if '(A)' in player[keys.entity_name]:
                            player[keys.entity_name] = player[keys.entity_name].split('(A)')[0].strip()
                        if '(C)' in player[keys.entity_name]:
                            player[keys.entity_name] = player[keys.entity_name].split('(C)')[0].strip()
                            player[keys.entity_captain] = True 
                        if '\n' in player[keys.entity_name]:
                            player[keys.entity_name] = player[keys.entity_name].split('\n')[0]
                        s_tr = stable.cssselect('tr')[i+1]
                        player[keys.entity_jersey] = parse.csstext(s_tr.cssselect('td.number-col')[0]) 
                        player[keys.entity_position] = parse.csstext(s_tr.cssselect('td.position-col')[0])
                        player[keys.entity_height] = parse.csstext(s_tr.cssselect('td.height-col')[0])
                        player[keys.entity_shoots] = parse.csstext(s_tr.cssselect('td.shoots-col')[0])                    
                        player[keys.entity_weight] = parse.csstext(s_tr.cssselect('td.weight-col')[0])
                        player[keys.entity_dob] = parse.csstext(s_tr.cssselect('td.birthdate-col span')[0])
                        player[keys.entity_origin] = parse.csstext(s_tr.cssselect('td.hometown-col')[0])
                    except Exception as e:
                        print 'yo:', e
                    
                    team['players'].append(player)
        return team

    @defer.inlineCallbacks
    def get_teams(self):    
        teams = []
        for team in self.seed:
            print team['link']
            teams.append(team)
            yield self.cv.goto_url(str(team['link']))
            url = self.cv.page().url().toString()
            if url[-1] != '/':
                url = url + '/'  
            print 'url:', url           
            yield self.cv.goto_url(url + 'roster').addCallback(self.cv.to_html).addCallback(self.process_players, team) 
            print 'done:', len(team['players'])
        defer.returnValue(self.teams_to_players(teams))

    def entities(self):
        print 'nhl started'         
        d = self.get_teams()
        d.addErrback(self.error_league)
        return d