import os
os.environ['QTDISPLAY'] = ':2'

from qt import qt5
print 'brasil:', qt5.qt_version

from qt.view import ChromeView
from twisted.internet import defer, reactor
from league import league_shared

from app import keys, parse

cv = ChromeView()

class BRASIL(league_shared.SharedLeague):
    
    def team_loop(self, trs):
        print 'team loop trs:', len(trs)
        teams = []
        for tr in trs[1:][:-1]:
            #print etree.tostring(tr)            
            team = {}
            team[keys.entity_standing] = parse.csstext(tr[0])[:-2]
            team[keys.entity_icon] = tr[1].cssselect('img')[0].attrib['src']
            team[keys.entity_name] = parse.csstext(tr[2][0])
            team[keys.entity_points] = parse.csstext(tr[3])
            team[keys.entity_points] = parse.csstext(tr[3])
            teams.append(team)
        '''
        <tr>
            <td valign="top" style="font-weight: bold; color: #006225 ">1</td>
            <td valign="middle" style="text-align: center; border-right: none; ">
                                <img height="20" onerror="this.src='http://www.cbf.com.br/imagens/escudos/empty.jpg';" src="http://cdn.cbf.com.br/cbf/imagens/escudos/00009rs.jpg">
                            </td>
            <td valign="middle" style="text-transform: uppercase; border-left: none; padding-left: 0" class="table-standings-col-club fittext">
                                <span>Internacional - RS </span>
                            </td>
            <td valign="top" style="font-weight: bold">16</td>
            <td valign="top">7</td>
            <td valign="top">5</td>
            <td valign="top">1</td>
            <td valign="top">1</td>
            <td valign="top">8</td>
            <td valign="top">3</td>
            <td valign="top">5</td>
            <td valign="top">3</td>
            <td valign="top">2</td>
            <td valign="top">0</td>
            <td valign="top">1</td>
            <td valign="top">26</td>
            <td valign="top">1</td>
            <td valign="top">76</td>
        </tr>
        '''        
        return teams
    
    def get_players(self, html, team):
        print 'get players', team
    
    @defer.inlineCallbacks
    def check_wikipedia(self, html, team):
        if len(html.xpath('.//a[@href="#Current_squad"]')) > 0:
            print 'set team link!'
            team['link'] = cv.page().url().toString()
            d = cv.to_html()
            d.addCallback(self.get_players, team)
            yield d 

    @defer.inlineCallbacks
    def wikipedia(self, teams):
        for team in teams:
            cites = yield cv.google(team[keys.entity_name] + " Current Squad site:wikipedia.org", results=3, domain="en.wikipedia.org")
            print team[keys.entity_name], cites
            for cite in cites:
                if not 'link' in team.keys():
                    d = cv.goto_url(cite)
                    d.addCallback(cv.to_html)
                    d.addCallback(self.check_wikipedia, team)
                    d.addErrback(self.error_league)
                    yield d
        defer.returnValue(teams)        

    @defer.inlineCallbacks
    def entities(self):
        cv.show()
        d = cv.goto_url('http://www.cbf.com.br/tournaments/brazilian-championship-division-a/teams/2016')
        d.addCallback(lambda ign: cv.goto_url('http://www.cbf.com.br/tournaments/brazilian-championship-division-a/standings/2016'))
        d.addCallback(cv.to_html)
        d.addCallback(lambda html: html.cssselect('table.table-standings tr'))
        d.addCallback(self.team_loop)
        d.addCallback(self.wikipedia)
        teams = yield d
        defer.returnValue(teams)        

if __name__ == '__main__':
    bs = BRASIL()
    reactor.callWhenRunning(bs.process_entities, pretty=True)
    reactor.run()
