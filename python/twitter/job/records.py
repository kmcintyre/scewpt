# -*- coding: utf-8 -*-
import os
#os.environ['QTDISPLAY'] = ':2'
from qt import qt5
print 'records:', qt5.qt_version

from app import keys, parse
from amazon.dynamo import Entity
from twisted.internet import defer, reactor, task

from qt.view import ChromeView

cv = ChromeView()
cv.setFixedWidth(1024)
cv.setFixedHeight(768)
cv.show()

def fbs_team_abbr(team_name):
    return team_name.lower().replace(' ', '-').replace('(', '').replace(')', '').replace("'", '').replace('&','')

def fbs_get_team(teams, fb_team_href):
    return [t for t in teams if fbs_team_abbr(t._data[keys.entity_profile].split(':', 1)[1]) == fb_team_href ][0]

@defer.inlineCallbacks
def fbs_standings(): 
    teams = [t for t in Entity().query_2(index=Entity.index_site_profile, site__eq='d1tweets.com', profile__beginswith='team:')]
    standings_html = yield cv.goto_url('http://www.espn.com/college-football/standings').addCallback(cv.to_html)
    for td in standings_html.cssselect('tr.standings-row td.team'):
        record = parse.csstext(td.getnext().getnext().getnext().getnext())
        fb_team_href = td.cssselect('a')[0].attrib['href'].rsplit('/', 1)[1]
        try:
            team = fbs_get_team(teams, fb_team_href)
            team[keys.entity_record] = record
            print team[keys.entity_profile].split(':', 1)[1], record
            team.partial_save()            
        except:
            print 'no such luck:', fb_team_href
    
    rankings_html = yield cv.goto_url('http://www.espn.com/college-football/rankings').addCallback(cv.to_html)
    try:
        for h2 in rankings_html.cssselect('h2.table-caption'):
            if parse.csstext(h2) == 'AP Top 25':
                for r in h2.getparent().cssselect('table')[0].cssselect('span.number'):
                    fb_team_href = r.getparent().getnext().cssselect('a.logo')[0].attrib['href'].rsplit('/', 1)[1]
                    team = fbs_get_team(teams, fb_team_href)
                    team[keys.entity_rank] = parse.csstext(r)
                    team.partial_save()
    except Exception as e:
        print 'e:', e
        
@defer.inlineCallbacks
def nfl_standings():
    nfl_standings = yield cv.goto_url('http://www.espn.com/nfl/standings').addCallback(cv.to_html)
    for span in nfl_standings.cssselect('span span.team-names'):
        td = span.getparent().getparent().getparent()
        wins = parse.csstext(td.getnext())
        losses = parse.csstext(td.getnext().getnext())
        ties = parse.csstext(td.getnext().getnext().getnext())
        tn = parse.csstext(span)
        try:
            record = wins + '-' + losses + '-' + ties
            t = Entity().get_item(league='nfl', profile='team:' + tn)
            t[keys.entity_record] = record
            print tn, record
            t.partial_save() 
        except Exception as e:
            print e
            
@defer.inlineCallbacks
def nhl_standings():
    nhl_standings = yield cv.goto_url('https://www.nhl.com/standings').addCallback(cv.to_html)    
    for span in nhl_standings.cssselect('a span.team--name'):
        try:
            tn = parse.csstext(span)
            td = span.getparent().getparent().getparent()
            wins = parse.csstext(td.getnext().getnext())
            losses = parse.csstext(td.getnext().getnext().getnext())
            ot = parse.csstext(td.getnext().getnext().getnext().getnext())
            record = wins + '-' + losses + '-' + ot
            for t in Entity().query_2(league__eq='nhl', profile__beginswith='team:' + tn):
                t[keys.entity_record] = record
                print tn, record
                t.partial_save() 
        except Exception as e:
            print e

@defer.inlineCallbacks
def nba_standings():
    nba_standings = yield cv.goto_url('http://www.espn.com/nba/standings').addCallback(cv.to_html)    
    for span in nba_standings.cssselect('span span.team-names'):
        try:
            tn = parse.csstext(span)
            td = span.getparent().getparent().getparent()
            wins = parse.csstext(td.getnext())
            losses = parse.csstext(td.getnext().getnext())
            record = wins + '-' + losses
            found = False
            for t in Entity().query_2(league__eq='nba', profile__eq='team:' + tn):
                found = True
                t[keys.entity_record] = record
                print tn, record
                t.partial_save()
            if not found:
                print 'missing:', tn 
        except Exception as e:
            print e            
    
@defer.inlineCallbacks
def mls_standings():
    mls_standings = yield cv.goto_url('https://www.mlssoccer.com/standings').addCallback(cv.to_html)    
    for td in mls_standings.cssselect('td[data-title="Club"]'):
        try:
            tn = parse.csstext(td.xpath('a[position() = last()]')[0])
            wins = parse.csstext(td.getparent().cssselect('td[data-title="Wins"]')[0])
            losses = parse.csstext(td.getparent().cssselect('td[data-title="Losses"]')[0])
            ties = parse.csstext(td.getparent().cssselect('td[data-title="Ties"]')[0])
            record = wins + '-' + losses + '-' + ties
            found = False
            for t in Entity().query_2(league__eq='mls', profile__eq='team:' + tn):
                found = True
                t[keys.entity_record] = record
                print tn, record
                t.partial_save()
            if not found:
                print 'missing:', tn             
        except Exception as e:
            print e    


@defer.inlineCallbacks
def fc_standings(league_name, urls, teams, sub = {}):
    print 'league:', league_name, 'team length:', len(teams)
    for url in urls:
        fc_standings_html = yield cv.goto_url(url).addCallback(cv.to_html)
        print 'fc_standings html length:', len(fc_standings_html), url, cv.page().url().toString()
        team_tds = fc_standings_html.cssselect('tr.standings-row')
        print 'team tds:', len(team_tds)
        for i, team_td in enumerate(team_tds):
            rank = i + 1
            try:
                tn = parse.csstext(team_td.cssselect('span.team-names')[0])
                if tn in sub:
                    #print 'sub:', tn, sub[tn]
                    tn = sub[tn]
                
                wdl = team_td.cssselect('td[style="white-space:no-wrap;"]')
                wins = parse.csstext(wdl[0])
                ties = parse.csstext(wdl[1])
                losses = parse.csstext(wdl[2])

                record = wins + '-' + losses + '-' + ties
                print 'team:', tn, 'record:', record
                found = False
                for t in Entity().query_2(league__eq=league_name, profile__eq='team:' + tn):
                    found = True
                    t[keys.entity_record] = record
                    t[keys.entity_rank] = rank
                    print tn, rank, record
                    t.partial_save()
                if not found:
                    for t2 in Entity().query_2(league__eq=league_name, profile__beginswith='team:' + tn):
                        found = True
                        t2[keys.entity_record] = record
                        t2[keys.entity_rank] = rank
                        print tn, rank, record
                        t2.partial_save()
                if not found:
                    try:
                        potential_teams = [t3 for t3 in teams if tn in t3[keys.entity_profile]]
                        if len(potential_teams) == 1:
                            found = True
                            potential_teams[0]
                            potential_teams[0][keys.entity_record] = record
                            potential_teams[0][keys.entity_rank] = rank
                            print tn, rank, record
                            potential_teams[0].partial_save()
                    except:
                        pass
                if not found:
                    print '    missing:', tn, rank


                
            except Exception as e:
                print 'fc exception:', e
            #<span class="team-names">Barcelona</span>
        '''    
        
            try:
                if len(team_td.cssselect('a')) > 0:
                    tn = parse.csstext(team_td.cssselect('a')[0])
                else:
                    tn = parse.csstext(team_td)
                if tn in sub:
                    #print 'sub:', tn, sub[tn]
                    tn = sub[tn]
                rank = parse.csstext(team_td.getprevious())
                 
                wins = parse.csstext(team_td.getnext().getnext().getnext())
                ties = parse.csstext(team_td.getnext().getnext().getnext().getnext())
                losses = parse.csstext(team_td.getnext().getnext().getnext().getnext().getnext())
                            
                            except Exception as e:
                print e
        '''      
bpl_sub = {
    'Brighton & Hove Albion': 'Brighton and Hove Albion'
    }
@defer.inlineCallbacks
def bpl_standings():
    teams = [t for t in Entity().query_2(league__eq='bpl', profile__beginswith='team:')]
    yield fc_standings('bpl', ['http://www.espn.com/soccer/table/_/league/eng.1', 'http://www.espn.com/soccer/table/_/league/eng.2'], teams, bpl_sub)

ligue1_sub = {
    'Dijon FCO': 'FCO Dijon', 'Stade Rennes': 'Stade Rennais FC', 'St Etienne': 'AS Saint-Étienne', 'Stade de Reims': 'Stade Reims',
    'Nimes': 'Nîmes Olympique', 'Le Havre AC': 'AC Le Havre', 'Chateauroux': 'LB Châteauroux', 'AS Nancy Lorraine': 'AS Nancy-Lorraine',
    'Orléans': 'US Orléans', 'Bourg-Peronnas': 'Bourg-en-Bresse Péronnas 01'
    }
@defer.inlineCallbacks
def ligue1_standings():
    teams = [t for t in Entity().query_2(league__eq='ligue1', profile__beginswith='team:')]
    yield fc_standings('ligue1', ['http://www.espn.com/soccer/table/_/league/fra.1', 'http://www.espn.com/soccer/table/_/league/fra.2'], teams, ligue1_sub)

laliga_sub = {
    'Barcelona': 'FC Barcelona', 'Celta Vigo': 'RC Celta', 'Atletico Madrid': 'Atlético de Madrid',
    'Deportivo La Coruña': 'RC Deportivo', 'Alavés': 'D. Alavés', 'Athletic Bilbao': 'Athletic Club',
    'Real Valladolid': 'R. Valladolid CF', 'Sporting Gijón': 'R. Sporting', 'Real Oviedo': 'R. Oviedo', 'AD Alcorcon': 'AD Alcorcón', 'Real Zaragoza': 'R. Zaragoza',
    'Gimnastic de Tarragona': 'Nàstic', 'Almeria': 'UD Almería', 'Sevilla Atletico': 'Sevilla FC', 'Cordoba': 'Córdoba CF',
    'Leganes': 'CD Leganés', 'Reus Deportiu': 'CF Reus', 'La Hoya Lorca': 'Lorca FC'
    }
@defer.inlineCallbacks
def laliga_standings():
    teams = [t for t in Entity().query_2(league__eq='laliga', profile__beginswith='team:')]
    yield fc_standings('laliga', ['http://www.espn.com/soccer/table/_/league/esp.1', 'http://www.espn.com/soccer/table/_/league/esp.2'], teams, laliga_sub)
    
seriea_sub = {
    'Internazionale': 'Inter Milan', 'US Pescara': 'Delfino Pescara 1936'    
    }
@defer.inlineCallbacks
def seriea_standings():
    teams = [t for t in Entity().query_2(league__eq='seriea', profile__beginswith='team:')]
    yield fc_standings('seriea', ['http://www.espn.com/soccer/table/_/league/ita.1', 'http://www.espn.com/soccer/table/_/league/ita.2'], teams, seriea_sub)

primeira_sub = {
    'Benfica': 'SL Benfica', 'Braga': 'SC Braga', 'Maritimo': 'CS Marítimo', 'Guimaraes': 'Vitória Guimarães SC', 'Paços de Ferreira': 'FC Paços de Ferreira',
    'Vitoria Setubal': 'Vitória Setúbal FC'
    }
@defer.inlineCallbacks
def primeira_standings():
    teams = [t for t in Entity().query_2(league__eq='primeira', profile__beginswith='team:')]
    yield fc_standings('primeira', ['http://www.espn.com/soccer/table/_/league/por.1'], teams, primeira_sub)

bundesliga_sub = {
        'Borussia Monchengladbach': 'Borussia Mönchengladbach', 'TSG Hoffenheim': 'TSG 1899 Hoffenheim', 'Bayer Leverkusen': 'Bayer 04 Leverkusen',
        'Hertha Berlin': 'Hertha BSC', 'Hamburg SV': 'Hamburger SV', 'FC Cologne': '1. FC Köln', 'Nurnberg': '1.FC Nuremberg',
        'St Pauli': 'FC St. Pauli', 'TSV Eintracht Braunschweig': 'Eintracht Braunschweig',
        '1. FC Heidenheim': '1.FC Heidenheim 1846', 'SpVgg Greuther Furth': 'SpVgg Greuther Fürth'
    }
@defer.inlineCallbacks
def bundesliga_standings():
    teams = [t for t in Entity().query_2(league__eq='bundesliga', profile__beginswith='team:')]
    yield fc_standings('bundesliga', ['http://www.espn.com/soccer/table/_/league/ger.1', 'http://www.espn.com/soccer/table/_/league/ger.2'], teams, bundesliga_sub)

rfpl_sub = {
    'Lokomotiv Moscow': 'Lokomotiv', 'Zenit St Petersburg': 'Zenit', 'CSKA Moscow': 'CSKA', 'Spartak Moscow': 'Spartak',
    'FC Arsenal Tula': 'Arsenal (Т)', 'Ural Sverdlovsk Oblast': 'Ural', 'Terek Grozny': 'Akhmat', 'FK Rubin Kazan': 'Rubin', 'FK Amkar Perm': 'Amkar',
    'FC Tosno': 'Tosno', 'Anzhi Makhachkala': 'Anji', 'Dinamo Moscow': 'Dynamo'
    }
@defer.inlineCallbacks
def rfpl_standings():
    teams = [t for t in Entity().query_2(league__eq='rfpl', profile__beginswith='team:')]
    yield fc_standings('rfpl', ['http://www.espn.com/soccer/table/_/league/rus.1'], teams, rfpl_sub)

csl_sub = {
    'Hebei China Fortune FC': 'Hebei China Fortune',
    'Beijing Guoan': 'Beijing Sinobo Guoan',
    'Chongqing Lifan': 'Chongqing Dangdai Lifan',
    'Yanbian Fude FC': 'Yanbian Funde',
    'Liaoning Whowin': 'Liaoning FC'
    }
@defer.inlineCallbacks
def csl_standings():
    teams = [t for t in Entity().query_2(league__eq='csl', profile__beginswith='team:')]
    yield fc_standings('csl', ['http://www.espn.com/soccer/table/_/league/chn.1'], teams, csl_sub)

    
@defer.inlineCallbacks
def ipl_standings():
    teams = [t for t in Entity().query_2(league__eq='ipl', profile__beginswith='team:')]
    ipl_standings = yield cv.goto_url('http://www.iplt20.com/stats').addCallback(cv.to_html)    
    for i, span in enumerate(ipl_standings.cssselect('span.standings-table__team-name.js-team')):
        try:
            td = span.getparent().getparent()
            #tn = parse.csstext(span)
            wins = parse.csstext(td.getnext().getnext())
            losses = parse.csstext(td.getnext().getnext().getnext())
            record = wins + '-' + losses
            rank = i+1
            fb_team_href = span.getparent().attrib['href'].rsplit('/', 1)[1]
            team = [t for t in teams if t[keys.entity_profile].split(':', 1)[1].lower().replace(' ','-') == fb_team_href][0]
            team[keys.entity_rank] = rank
            team[keys.entity_record] = record            
            print team[keys.entity_profile].split(':', 1)[1], rank, record
            team.partial_save()
            #for t in Entity().query_2(league__eq='nhl', profile__beginswith='team:' + tn):
            #    t[keys.entity_record] = record
            #    print tn, record
            #    t.partial_save() 
        except Exception as e:
            print e
            
mlb_sub = { 'nya': 'nyy', 'tba': 'tb', 'kca': 'kc', 'cha': 'cws', 'nyn' : 'nym', 'chn': 'chc', 'sln': 'stl', 'lan': 'la', 'sdn': 'sd', 'sfn': 'sf'}
            
@defer.inlineCallbacks
def mlb_standings():
    from league.scrape.mlb import MLB
    mlb_abbrv = MLB().abbr
    yield cv.goto_url('http://www.mlb.com/mlb/standings')
    yield task.deferLater(reactor, 2, defer.succeed, True)
    html = yield cv.to_html()
    for td in html.cssselect('td.dg-team_full'):
        a = td.cssselect('a')[0]
        wins = parse.csstext(td.getnext())
        losses = parse.csstext(td.getnext().getnext())
        record = wins + '-' + losses
        try:
            attrb = a.attrib['class']
            if attrb in mlb_sub:
                attrb = mlb_sub[attrb]
            t = Entity().get_item(league='mlb', profile = 'team:' + mlb_abbrv[attrb])
            t[keys.entity_record] = record
            print t[keys.entity_profile].split(':', 1)[1], record, attrb
            t.partial_save()            
        except Exception as e:
            print 'mlb exception:', e    

@defer.inlineCallbacks
def standings():
    yield fbs_standings()
    yield nfl_standings()
    yield nhl_standings()
    yield nba_standings()
    yield mls_standings()
    yield mlb_standings()
    yield laliga_standings()
    yield ligue1_standings()
    yield seriea_standings()
    yield primeira_standings()
    yield bundesliga_standings()
    yield rfpl_standings()        
    yield bpl_standings()
    yield csl_standings()
    yield ipl_standings()
    reactor.callLater(0, reactor.stop)
        
if __name__ == '__main__':
    reactor.callWhenRunning(standings)
    reactor.run()
