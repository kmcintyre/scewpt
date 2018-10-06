from league import league_shared

from twisted.internet import reactor, defer, task
from app import keys, fixed, parse, user_keys
from lxml import etree

ipl_base = 'http://www.iplt20.com'

class IPL(league_shared.TeamSportsLeague):
    
    min_size = 180
    max_size = 230        
    
    def key_lookup(self, key):
        if key == 'ipl debut':
            return keys.entity_debut
        elif key == user_keys.user_role:
            return keys.entity_position
        elif key == 'birth date':
            return keys.entity_dob
        return key
            
    def playerinfo(self, html, player):
        for key in html.cssselect('td[class="label"]'):
            if not parse.csstext(key).isnumeric():
                value = key.getnext() 
                player[self.key_lookup(parse.csstext(key).lower())] = parse.csstext(value)
        for key in html.cssselect('p[class="qsHeader"]'):
            value = key.getnext()
            player[self.key_lookup(key)] = parse.csstext(value)

    @defer.inlineCallbacks
    def loopplayers(self, team):
        for player in team['players']:
            d = self.cv.goto_url(player[keys.entity_profile])
            d = d.addCallback(self.cv.to_html)
            d.addCallback(self.playerinfo, player)
            yield d        
        team['players'] = [p for p in team['players'] if keys.entity_name in p.keys() and len(
            p[keys.entity_name]) > 2 and keys.entity_profile in p.keys()]
        print 'player length:', len(team['players'])        

    def getplayers(self, html, team):
        team['players'] = []
        for a in html.cssselect('a.squadPlayerCard'):
            print a
            #print 'hey:', player_span, player_span.cssselect('div.playerPhoto img')[0].attrib
            player = {}
            player[keys.entity_profile] = fixed.clean_url(ipl_base + a.attrib['href'])
            #print 'player 1:', player
            player[keys.entity_pic] = 'http://iplstatic.s3.amazonaws.com/players/210/' + a.cssselect('div.playerPhoto')[0].cssselect('img[data-player-id]')[0].attrib['data-player-id'] + '.png'
            #print 'player 2:', player 
            player[keys.entity_name] = parse.csstext(a.cssselect('p.player-name')[0])
            #print 'player 3:', player
            if len(a.cssselect('span.captain')) > 0:
                player[keys.entity_captain] = True 
            if len(a.cssselect('span.overseas-player')) > 0:
                player[keys.entity_foreign] = True
            if len(a.cssselect('span.wicket-keeper')) > 0:
                player[keys.entity_position] = "Wicket Keeper"                  
            for li in a.cssselect('ul.stats li'):
                label = parse.csstext(li.cssselect('span.label')[0])
                value = parse.csstext(li.cssselect('span.value')[0])                
                player[label.lower()] = value
            print player            
            team['players'].append(player)
        print 'length of team:', len(team['players'])
        return team

    @defer.inlineCallbacks
    def loopteams(self, teams):
        for team in teams:
            href = team['href']
            yield self.cv.goto_url(href + '/squad')
            yield task.deferLater(reactor, 5, defer.succeed, True)
            d = self.cv.to_html()            
            d.addCallback(self.getplayers, team)
            #d.addCallback(self.loopplayers)
            yield d
        defer.returnValue(teams)

    def getteams(self, html):        
        teams = []
        for team_anchor in html.cssselect('a.card.team-card'):            
            tn = ''
            for te in team_anchor.cssselect('h3.card__title'):
                tn = etree.tostring(te)
                tn = tn.replace('<br/>', ' ')
            tn = tn.split('>', 1)[1].split('<', 1)[0].strip()
            while '  ' in tn:
                tn = tn.replace('  ',' ')
            team = {'team': tn, 
                    'href': ipl_base + team_anchor.attrib['href']
                    }
            print team
            teams.append(team)
        return teams

    def entities(self):
        print 'entities'
        d = self.cv.goto_url('http://www.iplt20.com/teams')
        d.addCallback(self.cv.to_html)
        d.addCallback(self.getteams)
        d.addCallback(self.loopteams)
        d.addCallback(self.teams_to_players)
        d.addErrback(self.error_league)
        return d
