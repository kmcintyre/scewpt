from league import league_shared

from app import keys, fixed, parse
from twisted.internet import reactor, defer, task

from lxml import etree

nn2016 = [
    '224804',
    '72820',        
    '120467',        
    '124507',        
    '110895',        
    '59474',        
    '115367',        
    '38973',
    '1469'
]

november_nine = [
    '153786',
    '21473',
    '75760',
    '40109',
    '93433',
    '195908',
    '171103',
    '116855',
    '205562',                     
    '4549',
    '177935',
    '193916',
    '19945',
    '175397',
    '99433',
    '127207',
    '95066',
    '111182',
    '121355',
    '129198',
    '134630',
    '146095',
    '15094',
    '15335',
    '176422',
    '180',
    '21552',
    '23322',
    '24190',
    '31685',
    '32360',
    '3473',
    '3587',
    '36080',
    '36210',
    '41656',
    '44559',
    '45047',
    '47319',
    '62210',
    '65041',
    '65249',
    '6770',
    '76052',
    '7631',
    '88480',
    '91248',
    '93992',
    '97521',
    '99963']

poker_celebs = [
    '19085',
    '46807',
    '44021'
    '41263',
    '153250',
    '164',
    '112176',
    '119304',
    '134083',
    '1377',
    '14030',
    '1414',
    '148756',
    '14908',
    '156446',
    '174045',
    '191',
    '19505',
    '2063',
    '2134',
    '214',
    '21802',
    '240',
    '286',
    '287',
    '38931',
    '420',
    '4476',
    '4513',
    '62816',
    '94626',
    '93581']

lfs = [
    '170818',
    '170818'
    '4368',
    '98032',
    '103553',
    '98401',
    '86599',
    '98360',
    '48148',
    '222',
    '20856',
    '3677',
    '890',
    '2053',
    '1002',
    '17164',
    '2603',
    '17069',
    '406'
]

curent_event_winner = [
    '153786'
]
main_event_winners = [
    '52681',
    '159541',
    '38984',
    '121170',
    '95260',
    '61471',
    '44509',
    '13044',
    '14271',
    '3426',
    '275',
    '129',
    '122',
    '213'
    '201',
    '120',
    '266',
    '17296',
    '245',
    '218',
    '859',
    '142',
    '17442',
    '423',
    '17313'
]

must_haves = [nn2016, november_nine, poker_celebs, lfs, curent_event_winner, main_event_winners]

class BOOTH(league_shared.Common):

    def table(self):
        players = [{
            keys.entity_name: 'Andrew Feldman',
            'twitter': 'AFeldmanESPN',
            keys.entity_profile: fixed.clean_url('http://en.wikipedia.org/wiki/andrew_feldman_(poker_player)')
            }, 
            {
            keys.entity_name: 'The Hendon Mob',
            'twitter': 'thehendonmob',
            keys.entity_profile: fixed.clean_url('http://www.thehendonmob.com')
            },
            {
             keys.entity_name: 'World Poker Tour',
             'twitter': 'WPT',
             keys.entity_profile: fixed.clean_url('http://www.worldpokertour.com')
             },
             {
             keys.entity_name: 'Rio Las Vegas',
             'twitter': 'RioVegas',
             keys.entity_profile: fixed.clean_url('http://en.wikipedia.org/wiki/rio_all_suite_hotel_and_casino')
              },
             {
             keys.entity_name: 'Party Poker',
             'twitter': 'partypoker',
             keys.entity_profile: fixed.clean_url('http://www.partypoker.com/')
              },
             {
             keys.entity_name: 'European Poker Tour',
             'twitter': 'PokerStarsEPT',
             keys.entity_profile: fixed.clean_url('http://www.europeanpokertour.com')
              }]            
        return players
    
class POKER(league_shared.SharedLeague):

    rank_difference_filter = 2

    min_size = 3000
    max_size = 4000
    
    gamblers = []
    
    done = defer.Deferred()
    
    def cb(self, data):
        for i, p in enumerate(data):
            player = {}
            a = etree.fromstring(p[2]).cssselect('a')[0]
            player[keys.entity_profile] = str('http://www.wsop.com' + a.attrib['href']).lower()
                        
            player[keys.entity_name] = parse.csstext(a)
            player[keys.entity_bracelets] = p[3]
            player[keys.entity_rings] = p[4]
            player[keys.entity_cashes] = p[5]
            player[keys.entity_earnings] = p[6]
            
            player[keys.entity_rank] = i + 1           
            country = etree.fromstring(p[1]).cssselect('i')[0].attrib['title']
            if country:
                player[keys.entity_country] = country                         
            self.gamblers.append(player)            
        self.done.callback(True)
    
    @defer.inlineCallbacks
    def entities(self):
        self.gamblers.extend(BOOTH().table())
        yield self.cv.goto_url('http://www.wsop.com/players/').addCallback(lambda ign: task.deferLater(reactor, 5, defer.succeed, True))
        self.cv.page().runJavaScript('data', self.cb)
        yield self.done
        for l in must_haves:
            for pid in l:
                purl = 'http://www.wsop.com/players/profile/?playerid=' + pid
                if purl not in [g[keys.entity_profile] for g in self.gamblers]:
                    print purl
                    try:
                        html = yield self.cv.goto_url(purl).addCallback(self.cv.to_html)
                        missing_gambler = {}
                        missing_gambler[keys.entity_profile] = purl
                        missing_gambler[keys.entity_name] = parse.csstext(html.cssselect('div.iRight div.iRightContent h3')[0])
                        try:
                            missing_gambler[keys.entity_country] = html.cssselect('div.PPCountry')[0].cssselect('i')[0].attrib['title']
                        except:
                            pass
                        tr = html.cssselect('table[id="PPtotals"] tr')[0]
                        missing_gambler[keys.entity_bracelets] = parse.csstext(tr[0].cssselect('b')[0])
                        missing_gambler[keys.entity_rings] = parse.csstext(tr[1].cssselect('b')[0])
                        missing_gambler[keys.entity_cashes] = parse.csstext(tr[2].cssselect('b')[0])
                        missing_gambler[keys.entity_earnings] = parse.csstext(tr[3].cssselect('b')[0])
                        print 'missing:', missing_gambler
                        self.gamblers.append(missing_gambler)
                    except Exception as e:
                        print e
        defer.returnValue(self.gamblers)

    def filter_tweet(self, msg):
        if 'rank__change' in msg:
            return len([k for k in msg.keys() if '__' in k and k.split('__')[1] in ['remove', 'add', 'change']]) == 1                     
