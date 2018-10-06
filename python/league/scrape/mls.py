from league import league_shared
from app import keys, fixed

from lxml import html

from twisted.web.client import getPage
from twisted.internet import reactor, defer

class MLS(league_shared.TeamSportsLeague):
    
    chrome_scraper = False

    mls_url = 'http://www.mlssoccer.com/'

    def process_team(self, body, team):
        try:
            print 'process team:', team
            doc = html.document_fromstring(body)
            team_name = doc.xpath('/html/head/title')[0].text.split('|')[1].strip()
            team['team'] = team_name
            team['players'] = []
            trs = doc.xpath('//table[@class="views-table cols-9"]/tbody/tr')
            if len(trs) > 0:
                print 'length of table team:', len(trs)
                for tr in trs:
    
                    player = {}
                    player[keys.entity_jersey] = tr[0].text.strip()
                    player[keys.entity_position] = tr[1].text.strip()
                    player[keys.entity_name] = tr[2][0].text.strip()
                    player[keys.entity_profile] = fixed.clean_url(
                        team['link'] + tr[2][0].attrib['href'])
                    player[keys.entity_age] = tr[3].text.strip()
                    player[keys.entity_height] = tr[4].text.strip()
                    player[keys.entity_weight] = tr[5].text.strip()
                    player[keys.entity_origin] = tr[6].text.strip()
                    player[keys.entity_status] = tr[7].text.strip()
                    #print player
                    team['players'].append(player)
            else:
                lis = doc.xpath('//ul[@class="player_list list-reset"]/li')
                if len(lis) > 0:
                    for li in lis:
                        player = {}
                        player[keys.entity_jersey] = li.xpath('div[@class="player_info"]/span[@class="jersey"]')[0].attrib['data-jersey']
                        player[keys.entity_position] = li.xpath('div[@class="player_info"]/span[@class="position"]')[0].text
                        try:
                            player[keys.entity_age] = li.xpath(
                                'div[@class="player_info"]/div[@class="stats_container"]/div[@class="birthdate"]/span[@class="stat age"]')[0].text
                        except:
                            pass
                        try:
                            player[keys.entity_height] = li.xpath(
                                'div[@class="player_info"]/div[@class="stats_container"]/span[@class="stat height"]')[0].text
                        except:
                            pass
                        
                        try:
                            player[keys.entity_pic] = li.xpath(
                                'div[@class="rounded_image_container"]/a/img[@class="rounded_image"]')[0].attrib['src'].split('?')[0]
                        except:
                            pass
                        
                        try:
                            player[keys.entity_weight] = li.xpath(
                                'div[@class="player_info"]/div[@class="stats_container"]/span[@class="stat weight"]')[0].text
                        except:
                            pass
                        try:
                            for designation in  li.xpath('div[@class="player_info"]/span[@class="designation"]'):
                                if not keys.entity_designation in player:
                                    player[keys.entity_designation] = designation.text                                
                                else:
                                    player[keys.entity_designation] += ', ' + designation.text                            
                        except:
                            pass                    
                        try:
                            player[keys.entity_origin] = li.xpath(
                                'div[@class="player_info"]/div[@class="hometown"]')[0].text
                        except:
                            pass
                        player[keys.entity_name] = li.xpath('div[@class="player_info"]/div[@class="name"]/a[@class="name_link"]')[0].text.strip()
                        player[keys.entity_profile] = fixed.clean_url(team['link'] + li.xpath('div[@class="player_info"]/div[@class="name"]/a[@class="name_link"]')[0].attrib['href'])
                        
                        team['players'].append(player)
            print 'team:', team['team'], 'players length:', len(team['players'])
        except:
            print 'ops!'
        return team

    @defer.inlineCallbacks
    def get_teams(self, incoming):
        print 'get teams'
        outgoing = []
        print 'incoming length:', len(incoming)
        for team in incoming:
            link = team['link'] + '/players'
            print 'roster link', link
            d = getPage(link)
            d.addCallback(self.process_team, team)
            d.addErrback(self.error_league)
            try:
                team = yield d
                if len( team['players'] ) > 0:
                    outgoing.append(team)
            except:
                pass
        print 'outgoing:', len(outgoing)        
        defer.returnValue(outgoing)
        

    def get_team_links(self, body):
        print 'get team links'
        doc = html.document_fromstring(body)
        teams = []
        for tr in doc.xpath('//div[@id="comp-banner-collapse"]/div/a'):
            link = tr.attrib['href']
            if link.endswith('/'):
                link = link[:-1]
            if 'mlsatlanta2017' not in link and 'lafc.com' not in link:
                team = {}
                if link == 'http://www.portlandtimbers.com':
                    link = 'http://www.timbers.com'
                if link == 'http://www.orlandocitysoccer.com':
                    link = 'http://www.orlandocitysc.com'
                team['link'] = link
                print 'team link:', link
                teams.append(team)
        return teams
        #return defer.Deferred()

    def entities(self):
        d = getPage(MLS.mls_url)
        d.addCallback(self.get_team_links)
        d.addCallback(self.get_teams)
        d.addCallback(self.teams_to_players)        
        d.addErrback(self.error_league)
        return d