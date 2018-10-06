from league import league_shared
from app import fixed, keys

from amazon.dynamo import Entity

from lxml import html, etree
from twisted.internet import defer
from twisted.web.client import getPage

class MLB(league_shared.TeamSportsLeague):
    chrome_scraper = False
    
    size_min = 1000
    size_max = 1500
    
    abbr = {u'ana': u'Los Angeles Angels', u'phi': u'Philadelphia Phillies', u'tex': u'Texas Rangers', u'sea': u'Seattle Mariners', u'ari': u'Arizona Diamondbacks', u'pit': u'Pittsburgh Pirates', 'cws': u'Chicago White Sox', u'mil': u'Milwaukee Brewers', u'min': u'Minnesota Twins', u'mia': u'Miami Marlins', u'cle': u'Cleveland Indians', u'oak': u'Oakland Athletics', 'chc': u'Chicago Cubs', u'hou': u'Houston Astros', 'nym': u'New York Mets', 'nyy': u'New York Yankees', u'was': u'Washington Nationals', 'la': u'Los Angeles Dodgers', 'kc': u'Kansas City Royals', 'sf': u'San Francisco Giants', 'tb': u'Tampa Bay Rays', 'sd': u'San Diego Padres', u'atl': u'Atlanta Braves', u'bos': u'Boston Red Sox', u'det': u'Detroit Tigers', u'cin': u'Cincinnati Reds', u'tor': u'Toronto Blue Jays', 'stl': u'St. Louis Cardinals', u'bal': u'Baltimore Orioles', u'col': u'Colorado Rockies'}

    old_entity = []

    def lookup(self, oldid):
        if len(self.old_entity) == 0:
            for e in Entity().query_2(league__eq='mlb', profile__beginswith='http://'):
                self.old_entity.append(e)
        for oe in self.old_entity:
            if oe[keys.entity_profile].endswith(oldid):
                return oe        

    def decorate_player_svg(self, player, tweet):
        return self.strong(player[keys.entity_position])

    thumbsize = 256, 256

    def gather_active_roster(self, h, team):
        doc = html.document_fromstring(h)
        #/html/body/div[1]/div[3]/div[1]/section/div/section[1]/table
        team[keys.entity_team] = doc.cssselect('meta[property="og:site_name"]')[0].attrib['content']
        for t in doc.xpath('//table[@class="data roster_table"][@summary]'):
            
            for pt in t.xpath('preceding-sibling::h4'):
                position = pt.text
                if pt.text[-1] == 's':
                    position = pt.text[:-1]
                for player in t.xpath('tbody/tr[position() > 0]'):
                    #print etree.tostring(player)
                    try:
                        player_dict = {}
                        player_dict[keys.entity_position] = position
                        
                        player_dict[keys.entity_profile] = fixed.clean_url('http://m.mlb.com' + player[2].xpath('a/@href')[0])
                        if player[0].text:
                            player_dict[keys.entity_jersey] = player[0].text
                            if player_dict[keys.entity_jersey] == '42':
                                try:
                                    e = Entity().get_item(league='mlb', profile=player_dict[keys.entity_profile])
                                    player_dict[keys.entity_jersey] = e[keys.entity_jersey]
                                except:
                                    pass
                        player_dict[keys.entity_name] = player[2].xpath('a[starts-with(@href, "/player/")]')[0].text
                        try:
                            player_dict[keys.entity_status] = etree.tostring(player[2], method="text").strip().split('<br>')[1]
                            print 'has status:', player_dict[keys.entity_status]                             
                        except:
                            pass
                        player_dict[keys.entity_height] = player[4].text
                        player_dict[keys.entity_weight] = player[5].text
                        player_dict[keys.entity_born] = player[6].text
                        bt = player[3].text
                        player_dict['bats'] = bt.split("/")[0]
                        player_dict['throws'] = bt.split("/")[1]
                        #print player_dict
                        team['players'].append(player_dict)
                    except Exception as e:
                        print 'player exception:', e
        print 'team:', team['team'], 'players length:', len(team['players'])
        return team

    @defer.inlineCallbacks
    def scrape_teams(self):
        outgoing=[]
        for team_abbr in self.abbr.keys():
            print 'abbr:', team_abbr, 'team:', self.abbr[team_abbr]
            tl = 'http://mlb.mlb.com/team/roster_40man.jsp?c_id=' + str(team_abbr)
            print tl
            d = getPage(tl)
            d.addCallback(self.gather_active_roster, {'players': []})
            d.addCallback(lambda team: outgoing.append(team))
            yield d
        defer.returnValue(outgoing)

    def entities(self):        
        d = self.scrape_teams()
        d.addCallback(self.teams_to_players)
        d.addErrback(self.error_league)
        return d