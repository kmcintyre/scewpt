from league import league_shared
from app import keys, fixed, parse

from twisted.internet import reactor, defer, task
import pprint

class LALIGA(league_shared.TeamSportsLeague):
    
    can_have_empty_teams = True
    remove_lost_teams = True
    
    min_size = 800
    max_size = 1300   
    
    def playerinfo(self, html, player):
        player[keys.entity_name] = parse.csstext(html.cssselect('div[id="nombre"]')[0])        
        try:
            player[keys.entity_nickname] = parse.csstext(html.cssselect('h1[id="nickname"]')[0])
        except:
            pass
        try:
            dob = parse.csstext(html.cssselect('div[id="fecha_nacimiento"]')[0]).split(' ')[-1]
            player[keys.entity_dob] = dob.split('/')[1] + '/' + dob.split('/')[0] + '/' + dob.split('/')[2]
        except:
            pass
        try:
            player[keys.entity_origin] = parse.csstext(html.cssselect('div[id="lugar_nacimiento"]')[0]).split(': ', 1)[1]
        except:
            pass
        try:
            nationality = parse.csstext(html.cssselect('div[id="nacionalidad"]')[0]).split(': ', 1)[1]
            if nationality != 'Undefined':
                player[keys.entity_nationality] = nationality 
        except:
            pass     
        for data in html.cssselect('div[class="box-datos"] div[class="box-dato"] div[class="nombre"]'):
            dn = parse.csstext(data)
            dv = parse.csstext(data.getnext())
            if dn == 'Height':
                player[keys.entity_height] = dv
            elif dn == 'Weight':
                player[keys.entity_weight] = dv
            elif dn == 'Twitter' and dv:
                player[keys.entity_source_twitter] = dv
                if player[keys.entity_source_twitter].startswith('@'):
                    player[keys.entity_source_twitter] = player[keys.entity_source_twitter][1:]                  
            elif dn == 'Instagram' and dv:
                try:
                    player[keys.entity_source_instagram] = dv.split('/')[3]
                    if player[keys.entity_source_instagram].startswith('@'):
                        player[keys.entity_source_instagram] = player[keys.entity_source_instagram]
                except:
                    pass
            elif dn == 'International':
                if dv != 'No':
                    player[keys.entity_international] = dv
                
        print player                                

    @defer.inlineCallbacks
    def loopplayers(self, team):
        print 'loopplayers:', len(team['players'])
        for player in team['players']:
            print 'profile:', player[keys.entity_profile]
            d = self.cv.goto_url(player[keys.entity_profile])
            d.addCallback(lambda res: task.deferLater(reactor, 1, defer.succeed, res))
            d.addCallback(self.cv.to_html)
            d.addCallback(self.playerinfo, player)
            d.addErrback(self.error_league)
            yield d
        team['players'] = [p for p in team['players'] if keys.entity_name in p.keys() and len(p[keys.entity_name]) > 2 and keys.entity_profile in p.keys()]        

    def getplayers(self, html, team):
        print 'getplayers'
        team['team'] = parse.csstext(html.cssselect('div[class="cabecera-seccion"] span[class="titulo"]')[0])
        print team['team']        
        for tr in html.cssselect('div[class="rotar-tabla margen"] div[id="DataTables_Table_0_wrapper"] table[id="DataTables_Table_0"] tr')[1:]:
            #if parse.csstext(positions) != 'Coach':
            player = {keys.entity_position: parse.csstext(tr.cssselect('td')[0])}
            a = tr.cssselect('td')[1].cssselect('a')[0]
            player[keys.entity_profile] = fixed.clean_url(a.attrib['href'])
            player[keys.entity_pic] = a.cssselect('img')[0].attrib['src']
            try:
                jersey = parse.csstext(tr.cssselect('td')[2])
                if jersey:
                    player[keys.entity_jersey] = jersey 
            except:
                print 'no jersey'
            player[keys.entity_yellows] = parse.csstext(tr.cssselect('td')[15])
            player[keys.entity_reds] = parse.csstext(tr.cssselect('td')[16])
            player[keys.entity_goals] = parse.csstext(tr.cssselect('td')[18])
            
            team['players'].append(player)            
        print [p[keys.entity_profile] for p in team['players']]

    @defer.inlineCallbacks
    def loopteams(self, teams):
        for team in teams:
            href = team['href']
            print '    team href:', href
            yield self.cv.goto_url(href)
            task.deferLater(reactor, 5, defer.succeed, True)
            html = yield self.cv.to_html()
            self.getplayers(html, team)
            yield self.loopplayers(team)
        print 'teams:', len(teams)

    def getteams(self, html):
        teams = []
        for t in html.cssselect('div[class="equipos"] a'):
            teamname = parse.csstext(t)
            if teamname[:2] == 'R.':
                teamname = 'Real' + teamname[2:]
            team = {'href': t.attrib['href'], 'team': teamname, 'players': []}
            teams.append(team)        
        return teams

    @defer.inlineCallbacks
    def entities(self):
        teams = yield self.cv.goto_url('http://www.lfp.es/en').addCallback(self.cv.to_html).addCallback(self.getteams)
        pprint.pprint(teams)
        yield self.loopteams(teams)
        players = self.teams_to_players(teams)
        defer.returnValue(players)