from app import keys, fixed, parse
from league import league_shared
from league import keys_hollywood

from twisted.internet import reactor, defer

class HOLLYWOOD(league_shared.SharedLeague):
    
    min_size = 1900
    max_size = 2100
    
    def page_extract(self, html):
        actors = []
        for div in html.cssselect('div.lister-list div.lister-item.mode-detail'):            
            try:
                actor = {}
                actor[keys.entity_rank] = parse.csstext(div.cssselect('span.lister-item-index.unbold.text-primary')[0]).split('.')[0]
                actor[keys.entity_pic] = div.cssselect('div.lister-item-image a img')[0].attrib['src']
                actor[keys.entity_name] = parse.csstext(div.cssselect('h3.lister-item-header a')[0]).strip()
                actor[keys.entity_profile] = fixed.clean_url('http://www.imdb.com' + div.cssselect('div.lister-item-image a')[0].attrib['href'])
                actor[keys.entity_position] = parse.csstext(div.cssselect('p.text-muted.text-small')[0]).split('|')[0].strip()
                actor[keys_hollywood.noted] = parse.csstext(div.cssselect('p.text-muted.text-small a')[0]).strip()
                actor[keys_hollywood.noted_profile] = fixed.clean_url('http://www.imdb.com' + div.cssselect('p.text-muted.text-small a')[0].attrib['href'])
                print actor
                actors.append(actor)
            except Exception as e:
                print 'page_extract exception:', e
        return actors                  
            
    @defer.inlineCallbacks
    def entities(self):
        
        url = 'http://www.imdb.com/search/name?gender=male,female&ref_=nv_cel_m_3'
        start = 0
        people = []
        while start < 2000:
            next_url = url 
            if start > 1:
                next_url = url + '&start=' + str(start)
            print len(people), next_url
            d = self.cv.goto_url(next_url)
            d.addCallback(lambda ign: self.cv.to_html())
            d.addCallback(self.page_extract)
            d.addCallback(people.extend)
            d.addErrback(self.error_league)
            yield d
            start += 50    
        defer.returnValue(people)
    
    dvd = '''
        <svg width="31" height="44">
        <foreignObject x="0" y="0" width="31" height="44">
            <img width="31" height="44" xmlns="http://www.w3.org/1999/xhtml" src="%s"/>          
        </foreignObject>
        </svg>
        '''
    dvd_img = '''
        <img width="31" height="45" xmlns="http://www.w3.org/1999/xhtml" src="%s"/>          
        '''
    
    def drop_prevented(self, entity):
        try:
            if keys.entity_rank in entity.keys():
                del entity[keys.entity_rank]
                entity.partial_save()
        except Exception as e:
            print 'drop prevention exception:', e
    
    def filter_tweet(self, msg):
        if 'rank__change' in msg:
            return True
            '''
            a = int(msg['rank__change'].split('__')[0])
            b = int(msg['rank__change'].split('__')[1])
            if a < b:
                print 'negative difference'
                return True
            c = max(a, b)
            d = min(a, b)
            pd = c - d
            print 'rank difference:', pd
            if pd < 50:
                print 'not enough rank difference!'
            '''    
        return False