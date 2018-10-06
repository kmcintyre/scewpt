from league import league_shared

from twisted.internet import defer
from app import fixed, keys, parse

class NBA(league_shared.TeamSportsLeague):
    
    min_size = 300
    max_size = 800

    nba_url = 'http://www.nba.com'
    free_agent = str('  \x95 FA')

    def process_ind_player(self, body, player, team):
        #doc = html.document_fromstring(body)
        try:
            pass
            # player[keys.entity_position] = doc.xpath('//div[@class="plyrTmbPositionTeam"]')[0].text.split('-')[0].strip()
        except:
            pass
        team['players'].append(player)

    def process_team(self, doc, team):
        print 'process team'
        team['players'] = []
        for section in doc.cssselect('section.row.nba-player-index__row'):            
            for p in section.cssselect('section.nba-player-index__trending-item'):
                player = {}
                player[keys.entity_jersey] = parse.csstext(p.cssselect('span.nba-player-trending-item__number')[0])
                anchor = p.cssselect('a')[0]
                player[keys.entity_name] = anchor.attrib['title']
                player[keys.entity_profile] = fixed.clean_url(NBA.nba_url + anchor.attrib['href'])
                player[keys.entity_pic] = 'http:' + anchor.cssselect('div.nba-player-index__image div.nba-player-index__headshot_wrapper img')[0].attrib['data-src']
                player[keys.entity_position] = parse.csstext(p.cssselect('div.nba-player-index__details span')[0])
                player[keys.entity_height] = parse.csstext(p.cssselect('div.nba-player-index__details strong')[0]).split(' ')[0] + '\' ' + parse.csstext(p.cssselect('div.nba-player-index__details strong')[1]).split(' ')[0] + '\"'
                player[keys.entity_weight] = parse.csstext(p.cssselect('div.nba-player-index__details strong')[2])
                team['players'].append(player)
        print 'team:', team['team'], 'players length:', len(team['players'])
        return team

    @defer.inlineCallbacks
    def get_teams(self, teams):
        for team in teams:
            d = self.cv.goto_url(team['link']).addCallback(self.cv.to_html)
            d.addCallback(self.process_team, team)        
            yield d
        defer.returnValue(teams)

    def get_teams_links(self, doc):    
        teams = []
        for a in doc.cssselect('div.team__list_wrapper div.team__list a'):
            href = a.attrib['href']
            teams.append({'link': NBA.nba_url + href, 'team': parse.csstext(a) })
        print 'nba links:', teams
        return teams

    def entities(self):
        d = self.cv.goto_url(self.nba_url + '/teams').addCallback(self.cv.to_html)
        d.addCallback(self.get_teams_links)
        d.addCallback(self.get_teams)
        d.addCallback(self.teams_to_players)
        d.addErrback(self.error_league)
        return d