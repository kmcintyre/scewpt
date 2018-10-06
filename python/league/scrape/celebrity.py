from twisted.internet import defer
from twisted.web.client import getPage

from league import league_shared, keys_league
from amazon.dynamo import Entity

from app import fixed, keys, parse
from lxml import etree

class CELEBRITY(league_shared.SharedLeague):
    
    chrome_width = 1024
    chrome_height = 768
    chrome_fresh = False
    
    min_size = 500
    max_size = 750
    
    twitter_url = 'https://twittercounter.com/pages/100/'
    
    def decorate_player_svg(self, player, tweet):   
        return 'rank ' + self.strong(fixed.ordstr(int(player[keys.entity_rank])))    

    def check_cite(self, cite):
        if cite in self.profile_overrides.keys():
            print '    substitute cite:', cite, self.profile_overrides[cite]
            return self.profile_overrides[cite]
        return cite
    def is_born(self, html, maybeperson, url):
        try:
            maybeperson[keys.entity_name] = parse.csstext(html.cssselect('table[class="infobox biography vcard"] tr th span')[0])
        except:
            maybeperson[keys.entity_name] = parse.csstext(html.cssselect('h1[id="firstHeading"][class="firstHeading"]')[0])
        for th in html.cssselect('th'):
            if parse.csstext(th).lower() in ['born', 'date of birth']:
                try:
                    maybeperson[keys.entity_dob] = parse.csstext(th.getparent().cssselect('span[class="bday"]')[0]).replace(')','')
                except:
                    pass
                maybeperson[keys.entity_profile] = fixed.clean_url(url)                    
            
    @defer.inlineCallbacks
    def scrape_page(self, html, team):
        for li in html.cssselect('li[data-pos]'):
            ranking = li.attrib['data-pos']
            celebrity_handle = li.cssselect('div[class="clr"] div[class="name-bio"] a[class="uname"]')[0].attrib['href'][1:]
            name = parse.csstext(li.cssselect('div[class="clr"] div[class="name-bio"] a[class="name"] span')[0])
            partial = {keys.entity_rank: ranking, keys.entity_name: name}
            existing_league = None
            for count_e in Entity().query_2(index=Entity.index_twitter_league, twitter__eq=celebrity_handle):
                if count_e[keys.entity_league] != 'celebrity':
                    existing_league = count_e[keys.entity_league]
            if not existing_league:
                partial[keys.entity_twitter] = celebrity_handle
            else:
                print 'already in league:', existing_league
            cite = yield self.cv.google(name + ' wikipedia', results=1, domain='en.wikipedia.org')
            try:
                clean_cite = self.check_cite(fixed.clean_url(cite[0]))
                    
                print name, clean_cite, ranking                                
                html = yield getPage(str(clean_cite)).addCallback(etree.HTML)
                self.is_born(html, partial, clean_cite)
                if keys.entity_profile in partial.keys():
                    dob = ''
                    try:
                        dob = partial[keys.entity_dob]
                    except:
                        pass
                    print '{:5s}'.format(partial[keys.entity_rank]), '{:40s}'.format(partial[keys.entity_name]), '{:20s}'.format(celebrity_handle), dob
                    
                    team.append(partial)
                else:
                    print '    not born:', ranking, '{:40s}'.format('https://twitter.com/' + celebrity_handle), name                   
            except:
                print 'cite exception:', ranking, celebrity_handle, name
            
    @defer.inlineCallbacks
    def entities(self):
        self.profile_overrides = keys_league.get_profile_overrides(self.get_league_name())
        counter = ['', '100', '200', '300', '300', '400', '500', '600', '700', '800', '900']
        partials = []    
        for c in counter:
            url = self.twitter_url + c
            html = yield self.cv.goto_url(url).addCallback(lambda ign: self.cv.to_html())
            yield self.scrape_page(html, partials).addErrback(self.error_league)                        
        print 'top1000:', len(partials)
        defer.returnValue(partials)