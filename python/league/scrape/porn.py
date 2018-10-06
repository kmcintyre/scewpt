from league import league_shared, keys_porn
from app import keys, fixed, parse
from twitter import twitter_keys

from twisted.internet import defer

class PRODUCTION(league_shared.Common):

    def studio_detail(self, html, studio):
        try:
            info = html.cssselect('table.infobox')[0] 
            try:
                studio[keys.entity_name] = parse.csstext(info.cssselect('caption')[0])
            except:
                studio[keys.entity_name] = studio[keys.entity_company]
            try:
                studio[keys.entity_pic] = fixed.clean_url('http:' + info.cssselect('.logo a img')[0].attrib['src'])
            except:
                pass
            for th in info.cssselect('tr th'):
                if parse.csstext(th) == 'Website':
                    studio[keys.entity_website] = fixed.clean_url(th.getnext().cssselect('a')[0].attrib['href'])
        except:
            pass
        print 'studio:', studio
        return True

    @defer.inlineCallbacks
    def studio_profiles(self, studios):
        for studio in studios:            
            html = yield self.cv.goto_url(studio[keys.entity_profile]).addCallback(self.cv.to_html)
            self.studio_detail(html, studio)            
        defer.returnValue(studios)
        
    def get_studios(self, html):
        studios = []
        h2 = html.cssselect('span[id="Production_companies_that_do_not_include_male.E2.80.93male_and_male.E2.80.93transgender_sex_scenes"]')[0].getparent()
        h2_male = html.cssselect('span[id="Production_companies_that_include_male.E2.80.93male_sex_scenes"]')[0].getparent()
        el = h2
        while el != h2_male:
            el = el.getnext()
            for a in el.cssselect('li a'):
                studio = {
                    keys.entity_profile: fixed.clean_url('http://en.wikipedia.org' + a.attrib['href']), 
                    keys.entity_company: a.attrib['title'].replace(' (page does not exist)', ''),
                    keys.entity_name: a.attrib['title'].replace(' (page does not exist)', '')
                }
                studios.append(studio)
        return studios
    
    @defer.inlineCallbacks
    def entities(self):          
        html = yield self.cv.goto_url('https://en.wikipedia.org/wiki/List_of_pornographic_film_studios').addCallback(self.cv.to_html)
        studios = self.get_studios(html)
        profiles = yield self.studio_profiles(studios)
        defer.returnValue(profiles)

class PERFORMING(league_shared.Common):

    def get_2010s(self, html):
        performers = []        
        for li in html.cssselect('h2 span[id="2010s"]')[0].getparent().getnext().cssselect('ul li'):
            a = li.cssselect('a')[0]
            star = { keys.entity_profile: fixed.clean_url('http://en.wikipedia.org' + a.attrib['href']), keys.entity_name: a.attrib['title']}
            performers.append(star)
        return performers
    
    @defer.inlineCallbacks
    def entities(self):          
        html = yield self.cv.goto_url('https://en.wikipedia.org/wiki/List_of_pornographic_actresses_by_decade').addCallback(self.cv.to_html)
        performer = self.get_2010s(html)        
        defer.returnValue(performer)

class PORN(league_shared.SharedLeague):
    
    min_size = 800
    max_size = 1200    
    
    @defer.inlineCallbacks
    def entities(self):
        ans = [] 
        html = yield self.cv.goto_url('https://www.pornhub.com/pornstars/top?si=1').addCallback(self.cv.to_html)
        for div in html.cssselect('div.topPornstarsContainer div.sectionWrapper div[id="indexListContainer"]'):
            rank = parse.csstext(div.cssselect('li')[0])
            a = div.cssselect('li.index-title a')[0]
            profile = fixed.clean_url('https://www.pornhub.com' + a.attrib['href'])
            name = parse.csstext(a)
            number_of_videos = parse.csstext(div.cssselect('li')[2])
            video_views = twitter_keys.numTwitter(int(parse.csstext(div.cssselect('li')[3])))
            print rank, name, profile, number_of_videos, video_views
            star = {
                keys.entity_rank: rank,
                keys.entity_profile: profile,
                keys.entity_name: name,
                keys_porn.videos: number_of_videos,
                keys_porn.video_views: video_views
                }
            ans.append(star)
        
        try:
            p = PRODUCTION()
            p.cv = self.cv
            production = yield p.entities()
            ans.extend(production)
        except Exception as e:
            print 'production exception:', e
        try:
            p2 = PERFORMING()
            p2.cv = self.cv
            performing = yield p2.entities()
            ans.extend(performing)
        except Exception as e:
            print 'performing exception:', e            
        defer.returnValue(ans)