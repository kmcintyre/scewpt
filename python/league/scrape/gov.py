from league import league_shared

from app import keys, fixed, parse
from twisted.internet import defer

from twisted.web.client import getPage

from lxml import html, etree
from urlparse import urlparse
    
class WHITEHOUSE(league_shared.Common):
    
    def ovaloffice(self):
        whitehouse = []
        presidents_office = {
            keys.entity_name: 'The President of the United States',
            keys.entity_profile: fixed.clean_url('http://en.wikipedia.org/wiki/White_House'),
            keys.entity_twitter: 'POTUS'
        }
        whitehouse.append(presidents_office)
        
        dt = {}
        dt[keys.entity_team] = 'White House'
        dt[keys.entity_name] = 'Donald Trump'
        dt[keys.entity_position] = 'President'
        dt[keys.entity_profile] = 'http://www.donaldjtrump.com'
        dt[keys.entity_party] = 'Republican'
        dt[keys.entity_state] = 'New York'
        
        whitehouse.append(dt)
        
        vp = {}
        vp[keys.entity_team] = 'White House'
        vp[keys.entity_position] = 'Vice President'
        vp[keys.entity_state] = 'District of Columbia'
        vp[keys.entity_terms] = '1'
        vp[keys.entity_name] = 'Mike Pence'
        vp[keys.entity_profile] = fixed.clean_url('https://en.wikipedia.org/wiki/Vice_President_of_the_United_States')
        vp[keys.entity_party] = 'Republican'        
        vp[keys.entity_twitter] = 'VP'
        whitehouse.append(vp)
        
        mp = {}
        mp[keys.entity_team] = 'White House'
        mp[keys.entity_position] = 'Vice President'
        mp[keys.entity_state] = 'District of Columbia'
        mp[keys.entity_terms] = '1'
        mp[keys.entity_name] = 'Mike Pence'
        mp[keys.entity_profile] = 'http://en.wikipedia.org/wiki/Mike_Pence'
        mp[keys.entity_party] = 'Republican'        
        mp[keys.entity_twitter] = 'mike_pence'


        fl = {}
        fl[keys.entity_team] = 'White House'
        fl[keys.entity_position] = 'First Lady'
        fl[keys.entity_name] = 'Melania Trump'
        fl[keys.entity_profile] = 'http://en.wikipedia.org/wiki/Melania_Trump'
        fl[keys.entity_party] = 'Republican'
        fl[keys.entity_twitter] = 'MELANIATRUMP'        
        whitehouse.append(fl)
        
        fs = {}
        fs[keys.entity_team] = 'White House'
        fs[keys.entity_position] = 'First Son'
        fs[keys.entity_name] = 'Donald Trump Jr'
        fs[keys.entity_profile] = 'http://en.wikipedia.org/wiki/Donald_Trump_Jr.'
        fs[keys.entity_party] = 'Republican'
        fs[keys.entity_twitter] = 'DonaldJTrumpJr'        
        whitehouse.append(fs)
        
        fs2 = {}
        fs2[keys.entity_team] = 'White House'
        fs2[keys.entity_position] = 'First Son'
        fs2[keys.entity_name] = 'Eric Trump'
        fs2[keys.entity_profile] = 'http://en.wikipedia.org/wiki/Eric_Trump'
        fs2[keys.entity_party] = 'Republican'
        fs2[keys.entity_twitter] = 'EricTrump'        
        whitehouse.append(fs2)        
        
        fsil = {}
        fsil[keys.entity_team] = 'White House'
        fsil[keys.entity_position] = 'First Son-in-Law'
        fsil[keys.entity_name] = 'Jared Kushner'
        fsil[keys.entity_profile] = 'http://en.wikipedia.org/wiki/Jared_Kushner'
        fsil[keys.entity_party] = 'Republican'
        fsil[keys.entity_twitter] = 'jaredkushner'        
        whitehouse.append(fsil)        
        
        fd = {}
        fd[keys.entity_team] = 'White House'
        fd[keys.entity_position] = 'First Daughter'
        fd[keys.entity_name] = 'Ivanka Trump'
        fd[keys.entity_profile] = 'http://en.wikipedia.org/wiki/Ivanka_Trump'
        fd[keys.entity_party] = 'Republican'
        fd[keys.entity_twitter] = 'IvankaTrump'        
        whitehouse.append(fd)
        
        fd2 = {}
        fd2[keys.entity_team] = 'White House'
        fd2[keys.entity_position] = 'First Daughter'
        fd2[keys.entity_name] = 'Tiffany Trump'
        fd2[keys.entity_profile] = 'http://en.wikipedia.org/wiki/Tiffany_Trump'
        fd2[keys.entity_party] = 'Republican'
        fd2[keys.entity_twitter] = 'TiffanyATrump'        
        whitehouse.append(fd2)        

        cos = {}
        cos[keys.entity_team] = 'White House'
        cos[keys.entity_position] = 'Chief of Staff'
        cos[keys.entity_name] = 'John F. Kelly'
        cos[keys.entity_profile] = 'http://en.wikipedia.org/wiki/John_F._Kelly'
        cos[keys.entity_party] = 'Republican'        
        whitehouse.append(cos)        

        cd = {}
        cd[keys.entity_team] = 'White House'
        cd[keys.entity_position] = 'Communications Director'
        cd[keys.entity_name] = 'Anthony Scaramucci'
        cd[keys.entity_profile] = 'http://en.wikipedia.org/wiki/Anthony_Scaramucci'
        cd[keys.entity_party] = 'Republican'        
        cd[keys.entity_twitter] = 'Scaramucci'
        whitehouse.append(cd)        
        
        cs = {}
        cs[keys.entity_team] = 'White House'
        cs[keys.entity_position] = 'Chief Strategist'
        cs[keys.entity_name] = 'Steve Bannon'
        cs[keys.entity_profile] = 'http://en.wikipedia.org/wiki/Steve_Bannon'
        cs[keys.entity_party] = 'Republican'        
        cs[keys.entity_twitter] = 'SteveKBannon'
        whitehouse.append(cs)        
        
        ctop = {}
        ctop[keys.entity_team] = 'White House'
        ctop[keys.entity_position] = 'Chief Counsel'
        ctop[keys.entity_name] = 'Kellyanne Conway'
        ctop[keys.entity_profile] = 'http://en.wikipedia.org/wiki/Kellyanne_Conway'
        ctop[keys.entity_party] = 'Republican'        
        ctop[keys.entity_twitter] = 'KellyannePolls'
        whitehouse.append(ctop)
        
        sa = {}
        sa[keys.entity_team] = 'White House'
        sa[keys.entity_position] = 'Special Advisor'
        sa[keys.entity_name] = 'Stephen_Miller'
        sa[keys.entity_profile] = 'http://en.wikipedia.org/wiki/Stephen_Miller_(political_advisor)'
        sa[keys.entity_party] = 'Republican'        
        sa[keys.entity_twitter] = 'StephenMillerAL'
        whitehouse.append(sa)        
        
        ps = {}
        ps[keys.entity_team] = 'White House'
        ps[keys.entity_position] = 'Press Secretary'
        ps[keys.entity_name] = 'Sarah Sanders'
        ps[keys.entity_profile] = 'http://en.wikipedia.org/wiki/Sarah_Huckabee_Sanders'
        ps[keys.entity_party] = 'Republican'
        ps[keys.entity_twitter] = 'PressSec'
        whitehouse.append(ps)
        
        js = {
             keys.entity_team: 'White House',
             keys.entity_name: 'Jeff Sessions',
             keys.entity_position: 'Attorney General',
             keys.entity_twitter: 'jeffsessions',
             keys.entity_profile: fixed.clean_url('http://en.wikipedia.org/wiki/Jeff_Sessions')
              }
        whitehouse.append(js)
        sm = {}
        sm[keys.entity_team] = 'White House'
        sm[keys.entity_position] = 'Treasury Secretary'
        sm[keys.entity_name] = 'Steven Mnuchin'
        sm[keys.entity_profile] = 'http://en.wikipedia.org/wiki/Steve_Mnuchin'
        sm[keys.entity_party] = 'Republican'
        sm[keys.entity_twitter] = 'stevenmnuchin1'
        whitehouse.append(sm)
        
        rz = {}
        rz[keys.entity_team] = 'White House'
        rz[keys.entity_position] = 'Interior Secretary'
        rz[keys.entity_name] = 'Ryan Zinke'
        rz[keys.entity_profile] = 'http://en.wikipedia.org/wiki/Ryan_Zinke'
        rz[keys.entity_party] = 'Republican'
        rz[keys.entity_twitter] = 'SecretaryZinke'
        whitehouse.append(rz)
        
        sp = {}
        sp[keys.entity_team] = 'White House'
        sp[keys.entity_position] = 'Agriculture Secretary'
        sp[keys.entity_name] = 'Sonny Perdue'
        sp[keys.entity_profile] = 'http://en.wikipedia.org/wiki/Sonny_Perdue'
        sp[keys.entity_party] = 'Republican'
        sp[keys.entity_twitter] = 'SecretarySonny'
        whitehouse.append(sp)
        
        wr = {}
        wr[keys.entity_team] = 'White House'
        wr[keys.entity_position] = 'Commerce Secretary'
        wr[keys.entity_name] = 'Wilbur Ross'
        wr[keys.entity_profile] = 'http://en.wikipedia.org/wiki/Wilbur_Ross'
        wr[keys.entity_party] = 'Republican'
        wr[keys.entity_twitter] = 'SecretaryRoss'
        whitehouse.append(wr)
        
        whitehouse.append({ keys.entity_twitter: 'WhiteHouse', keys.entity_profile: 'team:White House'})
        
        return whitehouse    

class AMBASSADORS(league_shared.Common):
    
    def callbackExtractAmbassadors(self, h):
        ambassadors = []
        #/html/body/div[3]/div[3]/div[4]/table[1]
        doc = html.document_fromstring(h)
        table = doc.cssselect('h2 span[id="Current_U.S._ambassadors"]')[0].getparent()
        while table.tag != 'table':
            table = table.getnext()      
        for tr in table.cssselect('tr')[1:]:
            try:
                if len(tr) == 6:
                    a = {}
                    a[keys.entity_team] = 'Ambassadors'
                    a[keys.entity_country] = tr[0][1].text
                    a[keys.entity_name] = tr[2][0].text
                    a[keys.entity_profile] = fixed.clean_url('http://en.wikipedia.org' + tr[2][0].attrib['href'])
                    a[keys.entity_position] = 'Ambassador'
                    #print a
                    ambassadors.append(a)
                else:
                    pass
            except Exception as e:
                print 'ambassadors exception:', e
        ambassadors.append({keys.entity_twitter: 'AmerAmbassadors', keys.entity_profile: 'team:Ambassadors' })
        return ambassadors

    def entities(self):        
        d = getPage('https://en.wikipedia.org/wiki/Ambassadors_of_the_United_States')
        d.addCallback(self.callbackExtractAmbassadors)
        d.addErrback(self.error_league)
        return d

class KSTREET(league_shared.Common):
    
    def theinsiders(self):
        obama = {}
        obama[keys.entity_team] = 'K-Street'
        obama[keys.entity_position] = 'Former President'
        obama[keys.entity_state] = 'District of Columbia'
        obama[keys.entity_terms] = '2'
        obama[keys.entity_pic] = 'http://upload.wikimedia.org/wikipedia/commons/8/8d/President_Barack_Obama.jpg'
        obama[keys.entity_name] = 'Barack Obama'
        obama[keys.entity_profile] = 'http://en.wikipedia.org/wiki/Barack_Obama'
        obama[keys.entity_party] = 'Democratic'
        obama[keys.entity_prior_exp] = 'President'
        obama[keys.entity_college] = 'Harvard'
        obama[keys.entity_assumed_office] = 'January 20, 2009'
        obama[keys.entity_born] = 'August 4, 1961'

        biden = {}
        biden[keys.entity_team] = 'K-Street'
        biden[keys.entity_position] = 'Former Vice President'
        biden[keys.entity_state] = 'District of Columbia'
        biden[keys.entity_terms] = '2'
        biden[keys.entity_pic] = 'http://upload.wikimedia.org/wikipedia/commons/6/64/Biden_2013.jpg'
        biden[keys.entity_name] = 'Joe Biden'
        biden[keys.entity_profile] = 'http://en.wikipedia.org/wiki/Joe_Biden'
        biden[keys.entity_party] = 'Democratic'
        biden[keys.entity_prior_exp] = 'Senator'
        biden[keys.entity_college] = 'University of Delaware'
        biden[keys.entity_assumed_office] = 'January 20, 2009'
        biden[keys.entity_born] = 'November 20, 1942'
        biden[keys.entity_term_expires] = 'January 20, 2017'
        biden[keys.entity_twitter] = 'JoeBiden'
        
        pm = {}
        pm[keys.entity_team] = 'K-Street'
        pm[keys.entity_position] = 'Lobbyist'
        pm[keys.entity_name] = 'Paul Manafort'
        pm[keys.entity_profile] = 'http://en.wikipedia.org/wiki/Paul_Manafort'
        pm[keys.entity_party] = 'Republican'        
        pm[keys.entity_twitter] = 'PaulManafort'
             
        insiders = [
            obama,
            biden, 
            pm,
            {
            keys.entity_team: 'K-Street',
            keys.entity_name: 'Hillary Clinton',
            keys.entity_position: 'K-Street',
            keys.entity_party: 'Democratic',
            keys.entity_profile: fixed.clean_url('http://www.hillaryclinton.com')
            },
            {
            keys.entity_team: 'K-Street',
            keys.entity_name: 'John Boehner',
            keys.entity_position: 'Former Speaker of the House',
            keys.entity_twitter: 'SpeakerBoehner',
            keys.entity_profile: fixed.clean_url('http://en.wikipedia.org/wiki/John_Boehner')
            }, 
            {
            keys.entity_team: 'K-Street',
            keys.entity_name: 'Trevor Potter',
            keys.entity_position: 'Lawyer',
            keys.entity_twitter: 'thetrevorpotter',
            keys.entity_profile: fixed.clean_url('http://en.wikipedia.org/wiki/Trevor_Potter')
            },
            {
             keys.entity_team: 'K-Street',
             keys.entity_name: 'Jim De Mint',
             keys.entity_position: 'Leader of Tea Party',
             keys.entity_twitter: 'JimDeMint',
             keys.entity_profile: fixed.clean_url('http://en.wikipedia.org/wiki/Jim_DeMint')
             },
             {
             keys.entity_team: 'K-Street',
             keys.entity_name: 'John Dingell',
             keys.entity_position: 'Politician',
             keys.entity_twitter: 'JohnDingell',
             keys.entity_profile: fixed.clean_url('http://en.wikipedia.org/wiki/John_Dingell')
              },            
            {
             keys.entity_team: 'K-Street',
             keys.entity_name: 'Paul Ryan',
             keys.entity_position: 'Speaker of the House',
             keys.entity_twitter: 'SpeakerRyan',
             keys.entity_profile: fixed.clean_url('http://en.wikipedia.org/wiki/Speaker_of_the_United_States_House_of_Representatives')
              },
             {
                 keys.entity_team: 'K-Street',
                keys.entity_position: 'Former FBI Director',
                keys.entity_name: 'James Comey',
                keys.entity_profile: 'http://en.wikipedia.org/wiki/James_Comey',
                keys.entity_party: 'Independent',
                keys.entity_twitter: 'Comey',
                },
                  {
                      keys.entity_team: 'K-Street',
                      keys.entity_position: 'Attorney',
                      keys.entity_name:  'Andrew Puzder',
                    keys.entity_profile: 'http://en.wikipedia.org/wiki/Andrew_Puzder',
                    keys.entity_party: 'Republican',
                    keys.entity_twitter: 'AndyPuzder',
                }
            ]
        insiders.append({keys.entity_profile: 'team:K-Street', keys.entity_twitter: 'OpenSecretsDC'})
        return insiders

wikiwl = 'https://en.wikipedia.org/wiki/List_of_current_heads_of_state_and_government'

class WORLD_LEADERS(league_shared.Common):

    def pullteam(self, h, players = []):
        doc = html.document_fromstring(h)
        for tr in doc.cssselect('a[title="List of sovereign states"]'):
            tr = tr.getparent().getparent()            
            while tr.getnext() is not None:
                tr = tr.getnext()
                try:
                    country = parse.csstext(tr.cssselect('th a')[0])
                    if country:
                        for td in tr.cssselect('td'):
                            if len(td.cssselect('a')) == 2:
                                try:
                                    player = {}
                                    player[keys.entity_team] = 'World Leaders'
                                    player[keys.entity_position] = parse.csstext(td.cssselect('a')[0]).split('\xc2')[0]
                                    player[keys.entity_name] = parse.csstext(td.cssselect('a')[1])
                                    player[keys.entity_profile] = fixed.clean_url('http://en.wikipedia.org' + td.cssselect('a')[1].attrib['href'])
                                    player[keys.entity_country] = country
                                    players.append(player)
                                except Exception as e:
                                    print 'world leader exception:', e                        
                except Exception as e:
                    print 'world leader exception:', e
        players.append({keys.entity_twitter: 'UN', keys.entity_profile: 'team:World Leaders'})
        return players

    def entities(self):
        d = getPage(wikiwl)        
        d.addCallback(self.pullteam)
        d.addErrback(self.error_league)
        return d

wikipac = 'http://en.wikipedia.org/wiki/List_of_political_action_committees'

class PAC(league_shared.Common):

    def pullteams(self, h):
        players=[]
        doc = html.document_fromstring(h) 
        h3 = doc.cssselect('h3 ~ ul li')
        print 'h3 length:', len(h3)
        h2 = doc.cssselect('h2 ~ ul li')
        print 'h2 length:', len(h2)
        h3.extend(h2)
        for li in h3:
            player = {}
            try:
                player[keys.entity_team] = 'PAC'
                player[keys.entity_topic] = parse.csstext(li.getparent().getprevious().getchildren()[0])
                if player[keys.entity_topic] != 'External links':
                    try:
                        href = li.cssselect('a')[0].attrib['href']
                        if not urlparse(href).scheme and href:
                            href = 'http://en.wikipedia.org' + href
                        player[keys.entity_profile] = fixed.clean_url(href)                    
                        player[keys.entity_name] = parse.csstext(li.cssselect('a')[0])
                        if player[keys.entity_name] and player[keys.entity_profile]:
                            if player[keys.entity_name].rfind(' - ') > 0:
                                player[keys.entity_location] = player[keys.entity_name][player[keys.entity_name].rfind(' - ') + 3:]
                                player[keys.entity_name] = player[keys.entity_name][:player[keys.entity_name].rfind(' - ')]
                            #print player
                            players.append(player)
                    except Exception as e2:
                        print 'exception inner:', e2
            except: 
                pass
        players.append({keys.entity_profile: 'team:PAC', keys.entity_twitter: 'FEC'})
        return players

    def entities(self):
        d = getPage(wikipac)   
        d.addCallback(self.pullteams)
        d.addErrback(self.error_league)
        return d


class DEPARTMENTS(league_shared.Common):
    
    sw = ['National', 'Office of the', 'Federal', 'Office of', 'Director of', 'Department of the', 'Department of', 'United States']
    skip = ['http://www.whitehouse.gov']
    
    def callbackDepartments(self, h):
        departments = []
        doc = html.document_fromstring(h)
        for a in doc.cssselect('li a, h3 a'):
            department_name = parse.csstext(a).split('(')[0]
            for k in self.sw:
                if department_name.startswith(k):
                    department_name = department_name[len(k):]
                    department_name = department_name.strip()
            department_name = department_name.strip()
            department_url = fixed.clean_url(a.attrib['href'])
            if department_url not in self.skip: 
                department = { keys.entity_name: department_name, keys.entity_profile: department_url}
                department[keys.entity_team] = 'Departments'
                departments.append(department)
        departments.append({ keys.entity_profile: 'team:Departments', keys.entity_twitter: 'USGAO', keys.entity_name: 'Oversight Committee'})
        return departments
    
    def entities(self):
        d = getPage("https://www.loc.gov/rr/news/fedgov.html")
        d.addCallback(self.callbackDepartments)
        d.addErrback(self.error_league)
        return d

class HOUSE(league_shared.Common):
    
    def callbackExtractHouse(self, h):
        representatives = []
        doc = html.document_fromstring(h)
        table = doc.cssselect('h2 span[id="Voting_members_by_state"]')[0].getparent().getnext()
        trs = table.cssselect('tr')
        for tr in trs[1:]:
            try:
                congress = {}
                congress[keys.entity_team] = 'House of Representatives'
                s = parse.csstext(tr[0].cssselect("a")[0]).split(" ")[:-1]
                try:
                    s.remove(' at')
                    s.remove('At')
                except:
                    pass
                congress[keys.entity_state] = ' '.join(s)
                if congress[keys.entity_state].endswith(' at'):
                    congress[keys.entity_state] = congress[keys.entity_state][:-3]
                try:
                    congress[keys.entity_pic] = 'http:' + tr[1].cssselect("a img")[0].attrib['src']
                except:
                    pass
                congress[keys.entity_name] = tr[1].cssselect('span.vcard a')[0].text
                congress[keys.entity_profile] = fixed.clean_url('http://en.wikipedia.org' + tr[1].cssselect('span.vcard a')[0].attrib['href'])
                if len(tr) == 9:
                    congress[keys.entity_party] = parse.csstext(tr[3])
                elif len(tr) == 7:
                    congress[keys.entity_party] = representatives[-1][keys.entity_party]
                congress[keys.entity_prior_exp] = parse.csstext(tr[-5])
                congress[keys.entity_college] = parse.csstext(tr[-4])
                try:
                    ao = tr[-3].text
                    if '*' in ao:
                        ao = ao.replace('*', '')
                    congress[keys.entity_assumed_office] = ao.strip()
                except:
                    pass
                congress[keys.entity_born] = parse.csstext(tr[-1]).strip()
                
                representatives.append(congress)
                
            except:
                pass
        representatives.append({keys.entity_twitter: 'USHouseHistory', keys.entity_profile: 'team:House of Representatives' })        
        return representatives
        
    def entities(self):        
        d = getPage('https://en.wikipedia.org/wiki/Current_members_of_the_United_States_House_of_Representatives')        
        d.addCallback(self.callbackExtractHouse)
        d.addErrback(self.error_league)        
        return d
    
class SENATE(league_shared.Common):
    
    def get_party(self, tr):
        color = tr.cssselect('td')[0].attrib['style'].split(':')[1]        
        if color == '#E81B23':
            return 'Republican'
        elif color == '#3333FF':
            return 'Democratic'
        else:
            return 'Independent'        
    
    def callbackExtractSenate(self, h):
        senators = []
        doc = html.document_fromstring(h)
        try:
            trs = doc.cssselect('h2 span[id="Senators"]')[0].getparent()
            while trs.tag != 'table':
                trs = trs.getnext()                        
            trs = trs.cssselect('tr')
            state = None
            party = None
            for i, tr in enumerate(trs[1:]):
                if i % 2 == 0:
                    offset = 1
                    if len(tr.cssselect('td')) == 9:
                        party = self.get_party(tr)
                    if len(tr.cssselect('td')) == 8:
                        offset = 0
                    state = tr[offset][0].text
                else:
                    if len(tr.cssselect('td')) == 8:
                        party = self.get_party(tr)
                    offset = 0
                    if len(tr.cssselect('td')) == 7:
                        offset = -1
                senator = {}
                senator[keys.entity_team] = 'US Senate'
                senator[keys.entity_state] = state
                
                senator[keys.entity_pic] = fixed.clean_url('http:' + tr[1 + offset].cssselect('img')[0].attrib['src'])
                senator[keys.entity_name] = tr[2 + offset].cssselect('span.vcard a')[0].attrib['title']
                senator[keys.entity_profile] = fixed.clean_url('http://en.wikipedia.org' + tr[2 + offset].cssselect('span.fn a')[0].attrib['href'])
                senator[keys.entity_party] = party
                senator[keys.entity_born] = parse.csstext(tr[3 + offset].cssselect('span.bday')[0])
                senator[keys.entity_term_expires] = parse.csstext(tr[7 + offset]).split(' ')[-1]
                senators.append(senator)
        except Exception as e:
            print 'senate exception:', e
        senators.append({keys.entity_twitter: 'SenateHistory', keys.entity_profile: 'team:US Senate' })
        return senators
        
    def entities(self):        
        d = getPage('https://en.wikipedia.org/wiki/List_of_current_United_States_Senators')    
        d.addCallback(self.callbackExtractSenate)
        return d
    
class GOVERNORS(league_shared.Common):

    def callbackExtractGovernors(self, h):
        try:
            governors = []
            doc = html.document_fromstring(h)
            h2 = doc.cssselect('h2 span[id="State_governors"]')[0].getparent()
            while h2.tag != 'table':
                h2 = h2.getnext()
            #n = doc.xpath('/html/body/div[3]/div[4]/div[4]/div/table[1]')[0]
            for tr in h2.cssselect('tr'):
                g = {}            
                try:
                    
                    g[keys.entity_team] = 'Governors'
                    g[keys.entity_flag] = 'http:' + tr[0].xpath('div[1]/a/img')[0].attrib['src']
                    g[keys.entity_state] = tr[0].xpath('div[2]/a')[0].text
                    try:
                        g[keys.entity_pic] = 'http:' + tr[1].find('a').find('img').attrib['src']
                    except:
                        pass
                    g[keys.entity_name] = tr[2].cssselect('center span.vcard a')[0].attrib['title']
                    #t = tr[2].find(".//a")
                    g[keys.entity_profile] = fixed.clean_url('http://en.wikipedia.org' + tr[2].cssselect('center span.vcard a')[0].attrib['href'])                
                    g[keys.entity_party] = tr[4].find('a').text
                    g[keys.entity_prior_exp] = parse.csstext(tr[5])
                    g[keys.entity_assumed_office] = parse.csstext(tr[6])
                    g[keys.entity_term_expires] = parse.csstext(tr[7])
                    governors.append(g)
                except:
                    pass
            governors.append({ keys.entity_twitter: 'NatlGovsAssoc', keys.entity_profile: 'team:Governors'})
            return governors
        except Exception as e:
            print e
        
    def entities(self):        
        d = getPage('https://en.wikipedia.org/wiki/List_of_current_United_States_governors')
        d.addCallback(self.callbackExtractGovernors)
        return d

class GOV(league_shared.SharedLeague):
    
    chrome_scraper = False
    
    min_size = 1200
    max_size = 1600
    
    @defer.inlineCallbacks    
    def entities(self):
        gov = []
        
        house = yield HOUSE().entities()
        print 'house:', len(house)
        if len(house) < 400 or len(house) > 600:
            exit(-1)
        gov.extend(house)
        
        senate = yield SENATE().entities()
        if len(senate) < 95 or len(senate) > 105:
            exit(-1)
        print 'senate:', len(senate)
        gov.extend(senate)
            
        wh = WHITEHOUSE().ovaloffice()        
        print 'whitehouse:', len(wh)
        gov.extend(wh)        
        
        kstreet = KSTREET().theinsiders()
        print 'kstreet:', len(kstreet)
        gov.extend(kstreet)

        governors = yield GOVERNORS().entities()
        if len(governors) < 40 or len(governors) > 60:
            exit(-1)        
        print 'governors:', len(governors)
        gov.extend(governors)

        amb = yield AMBASSADORS().entities()
        print 'ambassadors:', len(amb)
        gov.extend(amb)               
        
        wl = yield WORLD_LEADERS().entities()
        print 'world leaders:', len(wl)
        gov.extend(wl)       
        
        pac = yield PAC().entities()
        print 'pac:', len(pac)
        gov.extend(pac)
        
        deps = yield DEPARTMENTS().entities()
        print 'departments:', len(deps)
        gov.extend(deps)
        defer.returnValue(gov)
