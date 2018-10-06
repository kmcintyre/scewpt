import os
os.environ['QTDISPLAY'] = ':2'

from qt import qt5
print 'bollywood:', qt5.qt_version

from league import league_shared

from twisted.internet import reactor, defer

from app import keys, fixed
from amazon.dynamo import Entity

class BOLLYWOOD(league_shared.SharedLeague):

    def extract_actors(self, res, teams):
        if res:
            print 'teams:', [t['team'] for t in teams]
            for tr in self.get_tw().web_page.mainFrame().documentElement().findAll('table[class="results"] tr').toList()[1:]:
                try:
                    actor = {}
                    actor[keys.entity_rank] = tr.findFirst(
                        'td[class="number"]').toInnerXml()[:-1]
                    actor[keys.entity_pic] = tr.findFirst(
                        'td[class="image"] a img').attribute('src')
                    actor[keys.entity_name] = tr.findFirst(
                        'td[class="name"] a').toInnerXml()
                    actor[keys.entity_profile] = fixed.clean_url(
                        'http://www.imdb.com' + tr.findFirst('td[class="name"] a').attrib['href'])
                    actor[keys.entity_position] = tr.findFirst(
                        'span[class="description"]').toInnerXml().split(',')[0].strip()
                    actor[keys.entity_noted] = tr.findFirst(
                        'span[class="description"] a').toInnerXml()
                    actor[keys.entity_noted_profile] = 'http://www.imdb.com' + \
                        tr.findFirst(
                            'span[class="description"] a').attrib['href']
                    if actor[keys.entity_position] not in [t['team'] for t in teams]:
                        print 'new team:', actor[keys.entity_position]
                        teams.append(
                            {'team': actor[keys.entity_position], 'players': []})
                    [t['players'].append(actor) for t in teams if t[
                        'team'] == actor[keys.entity_position]]
                except Exception as e:
                    print 'extract exception:', e
            return teams
        else:
            return defer.FAILURE

    def getactors(self, teams, start=1):
        if start < 2000:
            url = 'http://www.imdb.com/search/name?gender=male,female&ref_=nv_cel_m_3'
            if start > 1:
                url = url + '&start=' + str(start)
            d = self.get_tw().xmlrpc_goto_url(url)
            d.addCallback(self.extract_actors, teams)
            d.addCallback(lambda ign: self.getactors(teams, start + 50))
            return d
        else:
            return teams

    def entities(self):
        d = self.getactors([])
        return d
    
if __name__ == '__main__':
    reactor.callWhenRunning(BOLLYWOOD().process)
    reactor.run()