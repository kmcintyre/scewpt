from league import league_shared
from app import keys, fixed, parse

from lxml.cssselect import CSSSelector
from twisted.internet import defer

class UFC(league_shared.SharedLeague):
    
    min_size = 400
    max_size = 700
    
    default_entity_types = ['fighter']
    derived_entity_types = ['weightclass']
    
    def parse_fighter(self, html, p):
        p[keys.entity_pic] = 'http:' + html.cssselect('div[class="fighter-image"] img')[0].attrib['src']        
        p[keys.entity_summary] = parse.csstext(html.cssselect('td[id="fighter-skill-summary"]')[0])
        
        try:
            p[keys.entity_rank] = html.cssselect('span[class~="fighter-ranking"] cufon')[2].attrib['alt'].strip()            
        except Exception as e:
            print 'missing rank:', e
            
        try:
            p[keys.entity_record] = parse.csstext(html.cssselect('td[id="fighter-skill-record"]')[0])
        except Exception as e:
            print 'missing record:', e
        try:
            p[keys.entity_nickname] = parse.csstext(html.cssselect('td[id="fighter-nickname"]')[0])
        except Exception as e:
            print 'missing nickname', e
                     
        p[keys.entity_resides] = parse.csstext(html.cssselect('td[id="fighter-lives-in"]')[0])
        p[keys.entity_age] = parse.csstext(html.cssselect('td[id="fighter-age"]')[0])        
        p[keys.entity_height] = parse.csstext(html.cssselect('td[id="fighter-height"]')[0])
        p[keys.entity_weight] = parse.csstext(html.cssselect('td[id="fighter-weight"]')[0])
        p[keys.entity_reach] = parse.csstext(html.cssselect('td[id="fighter-reach"]')[0])
        print 'fighter:', p                    
        return defer.SUCCESS
        
    @defer.inlineCallbacks
    def search_ufc(self, players):
        print 'ufc_find:', len(players)
        for i, p in enumerate(players):
            print 'p:', i, 'of', len(players)
            if keys.entity_profile not in p.keys():
                search_term = p[keys.entity_name] + ' site:www.ufc.com'
                d = self.cv.bing(search_term)
                google_results = yield d
                print 'google results:', google_results
                try:
                    profile = [result for result in google_results if result.startswith('http://www.ufc.com/fighter')][0]
                    profile = profile.split('?')[0]
                    print 'profile:', profile
                    if not fixed.clean_url(profile).endswith('/media'):
                        p[keys.entity_profile] = fixed.clean_url(profile.replace('%20','')).lower()
                        d = self.cv.goto_url(p[keys.entity_profile])
                        d.addCallback(self.cv.to_html)
                        d.addCallback(self.parse_fighter, p)                    
                        yield d                    
                except:
                    print 'missing on ufc.com:', p[keys.entity_name]
        defer.returnValue([p for p in players if keys.entity_profile in p and 'weight_class' not in p[keys.entity_profile]])

    def scrape_divisions(self, html, divisions):
        print 'scrape_division:', divisions
        players = []
        mens = True
        for wc in divisions:        
            wccss = wc.replace(" ", "_").replace("'", ".27")
            if "Women's" in wc:
                mens = False
            wc = wc.replace("Women's ", "").capitalize()
            print 'team:', wc, wccss
            css_string = 'span[id^="' + wccss + '"]'
            print css_string        
            try:    
                css = CSSSelector(css_string)(html)[0]
            except:
                css_string = css_string.replace(wc.lower(), wc)
                print css_string
                css = CSSSelector(css_string)(html)[0]
            t = css.getparent()
            while t.tag != 'table':
                t = t.getnext()
            print 'finally:', t.tag
            for tr in t.findall('.//tr')[2:][:-1]:
                #print etree.tostring(tr)
                #country = parse.csstext(tr.findall('.//td')[0])                                    
                fighter = {}
                try:
                    fighter[keys.entity_nickname] = parse.csstext(tr.find('.//td[3]/i'))
                except:
                    pass
                
                fighter[keys.entity_gender] = 'Male' if mens else 'Female'               
                #fighter[keys.entity_origin] = country
                try:
                    a = tr.cssselect('td span.vcard span a')[0]
                    fighter[keys.entity_name] = parse.csstext(a)
                except:
                    fighter[keys.entity_name] = parse.csstext(tr.find('.//td[1]'))
                if '(C)' in parse.csstext(tr):
                    fighter['titleholder'] = 'yes'
                fighter[keys.entity_weightclass] = wc
                print fighter
                players.append(fighter)
        print 'done: figther len', len(players)
        return players

    def entities(self):
        print 'fighters'
        divisions = ['Heavyweights', 'Light heavyweights', 'Middleweights', 
                     'Welterweights', 'Lightweights', 'Featherweights', 
                     'Bantamweights', 'Women\'s bantamweights', 'Flyweights', 'Women\'s strawweights', 
                     'Women\'s featherweights']
        d = self.cv.goto_url('https://en.wikipedia.org/wiki/List_of_current_UFC_fighters')
        d.addCallback(self.cv.to_html) 
        d.addCallback(self.scrape_divisions, divisions)
        d.addCallback(self.search_ufc)
        d.addCallback(lambda players: [p for p in players if keys.entity_profile in p.keys()])        
        d.addErrback(self.error_league)
        return d
