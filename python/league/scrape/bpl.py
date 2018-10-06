from league import league_shared
from app import keys, parse
from twisted.internet import reactor, defer, task

class BPL(league_shared.TMSportsLeague):
    
    chrome_width = 1024
    chrome_height = 768
    
    divisions = [('https://www.transfermarkt.com/championship/startseite/wettbewerb/GB2', 'Clubs - Championship')]

    min_size = 800
    max_size = 1500

    can_have_empty_teams = True

    profile_prefix = '/en-gb/clubs/profile.overview.html/'
    bpl_url = 'http://www.premierleague.com'
    profile_remove_list = [
        'div[class="parbase bannerad"]', 'div[id="cookies-verify"]']

    def errback(self, err):
        print 'error:', err

    def update_player(self, html, player):
        for info in html.cssselect('div.personalLists ul li div.info'):
            label = parse.csstext(info.getprevious())
            if label == 'Weight':
                player[keys.entity_weight] = parse.csstext(info)
            elif label == 'Height':
                player[keys.entity_height] = parse.csstext(info)
            elif label == 'Date of Birth':
                player[keys.entity_dob] = parse.csstext(info)
            elif label == 'Age':
                player[keys.entity_age] = parse.csstext(info)
        print ''
        print player
        print ''

    @defer.inlineCallbacks
    def process_players(self, team):
        for player in team['players']:
            print 'player url:', player[keys.entity_profile]
            d = self.cv.goto_url(player[keys.entity_profile])
            d.addCallback(lambda res: task.deferLater(reactor, 1, defer.succeed, res))
            d.addCallback(self.cv.to_html)
            d.addCallback(self.update_player, player)
            d.addErrback(self.error_league)            
            yield d
        defer.returnValue(team)

    def add_players(self, html, team):
        for li in html.cssselect('ul.squadListContainer.squadList > li'):
            player = {}
            player[keys.entity_profile] = self.bpl_url + li.cssselect('a.playerOverviewCard')[0].attrib['href']
            player[keys.entity_name] = parse.csstext(li.cssselect('h4.name')[0])
            player[keys.entity_jersey] = parse.csstext(li.cssselect('span.number')[0])
            player[keys.entity_position] = parse.csstext(li.cssselect('span.position')[0])
            try:
                player[keys.entity_nationality] = parse.csstext(li.cssselect('li.nationality dl dd.info span.playerCountry')[0])
            except:
                pass
            for l in li.cssselect('ul.squadPlayerStats li dl dd.info'):
                label = parse.csstext(l.getprevious())
                if label == 'Appearances':
                    player[keys.entity_appearances] = parse.csstext(l)
                elif label == 'Goals':
                    player[keys.entity_goals] = parse.csstext(l)
                elif label == 'Assists':
                    player[keys.entity_assists] = parse.csstext(l)                    
            try:
                player[keys.entity_pic] = 'http:' + li.cssselect('img.statCardImg')[0].attrib['src']
            except:
                pass
            print 'player:', player
            team['players'].append(player)          

    @defer.inlineCallbacks
    def get_teams(self, incoming):
        outgoing = []
        print 'incoming length:', len(incoming)
        for link in incoming:
            url = link.rsplit('/', 1)[0] + '/squad'
            print 'squad link:', url
            yield self.cv.goto_url(url)
            yield task.deferLater(reactor, 3, defer.succeed, True)
            html = yield self.cv.to_html()
            team = {'team': parse.csstext(html.cssselect('h1.team.js-team')[0]).strip(), 'players': []}
            print 'team:', team            
            self.add_players(html, team)
            yield self.process_players(team)
            outgoing.append(team)
        p1 = self.teams_to_players([t for t in outgoing if 'players' in t and len(t['players']) > 0])
        p2 = yield self.transfermarket(self.cv)
        defer.returnValue(p1 + p2)        

    def get_team_links(self, html):
        links = []
        for team in html.cssselect('div.tableContainer')[0].cssselect('td.team'):
            new_href = 'http://www.premierleague.com' + team.cssselect('a')[0].attrib['href']
            if new_href not in links and new_href.count('www.premierleague.com') == 1:
                print 'team link:', new_href
                links.append(new_href)
        return links

    @defer.inlineCallbacks
    def entities(self):
        print self.bpl_url + '/tables'
        html = yield self.cv.goto_url(self.bpl_url + '/tables').addCallback(lambda res: task.deferLater(reactor, 2, defer.succeed, res)).addCallback(self.cv.to_html)
        links = self.get_team_links(html)
        teams = yield self.get_teams(links)
        defer.returnValue(teams)