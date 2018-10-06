from amazon import s3
from league import league_shared, keys_market
from app import keys, fixed, parse

from twisted.internet import defer, reactor, task

import json
from lxml import html
from os import listdir
from os.path import isfile, join

def store_data(datapath, data):
    s3.save_s3(s3.bucket_straight('ventorta.com'), datapath, json.dumps(data, indent = 4), None, 'application/json')

def load_data(datapath):
    maybe_key = s3.check_key(s3.bucket_straight('ventorta.com'), datapath)            
    if not maybe_key:
        store_data(datapath, [])
        return load_data(datapath)
    else:
        return json.loads(maybe_key.get_contents_as_string())
    
rt = { 
    0: 'mainframe',
    1: 'subframe',
    2: 'stylesheet',
    3: 'script',
    4: 'image',
    5: 'font',
    6: 'other',
    7: 'object',
    8: 'media',
    9: 'web worker',
    10: 'shared worker',
    11: 'prefetch',
    12: 'favicon',
    13: 'xhr',
    14: 'ping',
    15: 'service worker',
    16: 'csp',
    17: 'plugin',
    255: 'unknown'
}


class InterceptorObject(object):
    from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor

    class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
        
        def status(self, info):
            print '{:15s}'.format(info.requestMethod()), '{:20s}'.format(rt[info.resourceType()]), info.requestUrl().host()
            
        def interceptRequest(self, info):
            if 'crunchbase' not in info.requestUrl().host():
                info.block(True)
                #self.status(info)
            else:
                pass
                #self.status(info)
    interceptor = WebEngineUrlRequestInterceptor() 

#intercept = WebEngineUrlRequestInterceptor()

accelorators_dict = {
    'Alchemist Accelerator': 'alchemist-accelerator',
    '500 Startups': '500-startups',
    'Amplify.LA': 'amplify-la',
    'AngelPad': 'angelpad',
    'The Brandery': 'the-brandery',
    'Capital Factory': 'capital-factory',
    'Capital Innovators': 'capital-innovators',
    'Dreamit': 'dreamit-ventures',
    'gener8tor': 'gener8tor',
    'Healthbox': 'healthbox',
    'MassChallenge': 'masschallenge',
    'Matter': 'matter-ventures',
    'Mucker Capital': 'muckercapital',
    'StartX': 'stanfordstartx-fund',
    'SURGE Accelerator': 'surge-accelerator',
    'Techstars': 'techstars',
    'Y Combinator': 'y-combinator'
    }

show_more_js = """
    document.querySelector('a.mat-raised.mat-button[aria-label="Show More"]').click()
"""
#<a class="mat-raised mat-button" mat-button=""  tabindex="0" aria-disabled="false"><span class="mat-button-wrapper">
#                Show More
#              </span><div class="mat-button-ripple mat-ripple" matripple=""><div class="mat-ripple-element" style="left: -20.6572px; top: -39.9697px; height: 127.939px; width: 127.939px; transition-duration: 450ms; transform: scale(1);"></div></div><div class="mat-button-focus-overlay"></div></a>                        
             

class STARTUP(league_shared.TeamSportsLeague):
    
    chrome_width = 1440
    chrome_height = 900
    
    min_size = 2500
    max_size = 4500
    
    def get_company_details(self, company, doc):
        for dd in doc.cssselect('dd'):
            if 'has been closed' in parse.csstext(dd):
                company[keys.entity_closed] = True
        for h2 in doc.cssselect('h2'):
            if parse.csstext(h2) == 'Overview':
                for dt in h2.getparent().getnext().cssselect('div.definition-list.container dt'):
                    dd = dt.getnext()
                    dt_text = parse.csstext(dt)[:-1]
                    if dt_text.lower() == 'headquarters':                        
                        company[keys.entity_headquarters] = parse.csstext(dd)
                    elif dt_text.lower() == 'description':  
                        company[keys.entity_description] = parse.csstext(dd)
                    elif dt_text.lower() == 'founders':  
                        company[keys.entity_founders] = parse.csstext(dd)                        
                    elif dt_text.lower() == 'categories':  
                        company[keys.entity_sector] = parse.csstext(dd)                        
                    elif dt_text.lower() == 'website ':  
                        company[keys.entity_profile] = fixed.clean_url(parse.csstext(dd))
                                                
                    elif dt_text.lower() == 'social':
                        for a in dd.cssselect('a[data-icons]'):
                            if a.attrib['data-icons'] == keys.entity_facebook:
                                company[keys.entity_facebook] = fixed.clean_url(a.attrib['href']).rsplit('/', 1)[1]
                            if a.attrib['data-icons'] == keys.entity_twitter:
                                company[keys.entity_twitter] = fixed.clean_url(a.attrib['href']).rsplit('/', 1)[1]
                                if company[keys.entity_twitter].startswith('@'):
                                    company[keys.entity_twitter] = company[keys.entity_twitter][1:]
                            if a.attrib['data-icons'] == keys.entity_linkedin:
                                company[keys.entity_linkedin] = fixed.clean_url(a.attrib['href']).replace('http://www.linkedin.com/', '')
    @defer.inlineCallbacks                        
    def process_incubators(self):
        from PyQt5.QtCore import QUrl
        from PyQt5.QtCore import Qt
        companies = []
        startup_path = '/home/ubuntu/scewpt/etc/data/startup/'
        for filename in [f for f in listdir(startup_path) if isfile(join(startup_path, f))]:
            print filename
            datapath = 'startup/db/' + filename.split('.')[0] + '.json'
            fullpath = startup_path + filename            
            data = load_data(datapath)
            table = html.parse(fullpath).getroot().cssselect('table')[0]
            incubator = table.attrib['data-name']
            print 'incubator:', incubator
            data_updated = False
            for tr in table.cssselect('tr'):
                anchor = tr.cssselect('td')[1].cssselect('a')[0]
                company = {}
                company[keys.entity_name] = anchor.attrib['data-name']
                company[keys.entity_incubator] = incubator
                company[keys.entity_crunchbase] = fixed.clean_url('https://www.crunchbase.com' + anchor.attrib['data-permalink'])
                company[keys_market.crunchbase_followers] = anchor.attrib['data-follower-count']                    
                company[keys.entity_pic] = fixed.clean_url(anchor.attrib['data-image'])                
                if company[keys.entity_crunchbase] in [sc[keys.entity_crunchbase] for sc in data]:
                    scraped_company = [sc2 for sc2 in data if sc2[keys.entity_crunchbase] == company[keys.entity_crunchbase]][0]
                    scraped_company.update(company)
                    companies.append(scraped_company)
                    print 'found:', len(companies), incubator, scraped_company
                    print '    '                    
                else:
                    print 'goto:', company[keys.entity_crunchbase]
                    self.cv.page().load(QUrl('https' + company[keys.entity_crunchbase][4:]))
                    d = task.deferLater(reactor, 15, defer.succeed, True)
                    d.addCallback(self.cv.to_html)
                    startup_html = yield d 
                    self.get_company_details(company, startup_html)
                    print 'incubator:', incubator, 'company:', company                                                    
                    if keys.entity_profile in company or keys.entity_founders in company or keys.entity_description in company or keys.entity_closed in company:
                        if keys.entity_closed not in company:
                            if keys.entity_twitter in company:
                                try:
                                    twitter_html = yield self.cv.goto_url('https://twitter.com/' + company[keys.entity_twitter]).addCallback(self.cv.to_html)
                                    scraped_twitter = parse.csstext(twitter_html.cssselect('h2.ProfileHeaderCard-screenname.u-inlineBlock.u-dir')[0])[1:]
                                    if scraped_twitter != company[keys.entity_twitter]:
                                        print 'update twitter:', scraped_twitter, company[keys.entity_twitter]
                                        company[keys.entity_twitter] = scraped_twitter  
                                except Exception as e:
                                    print 'twitter lookup exception:', e
                                    del company[keys.entity_twitter]
                            if keys.entity_description in company:
                                del company[keys.entity_description]                                                                        
                        else:
                            print 'entity closed'
                            if keys.entity_profile in company:
                                try:
                                    del company[keys.entity_profile]
                                except:
                                    pass
                        data_updated = True
                        data.append(company)
                        companies.append(company)
                    elif len(startup_html.cssselect('section[id="main-content"] div[id="error-404"]')) > 0:
                        print '404'
                        data.append(company)
                        companies.append(company)
                    else:
                        print 'QUIT!'
                        if data_updated:                            
                            store_data(datapath, data)
                        reactor.stop()
            if data_updated:
                store_data(datapath, data)
            print 'DONE!'            
        defer.returnValue(companies)
                
    @defer.inlineCallbacks  
    def entities(self):
        from PyQt5.QtTest import QTest
        from PyQt5.QtCore import Qt
        from qt.qt5 import app
        accelators = []
        self.cv.page().profile().setRequestInterceptor(InterceptorObject().interceptor)
        try:
            for k in accelorators_dict.keys():
                print accelorators_dict[k]
                accelator = { keys.entity_profile: 'team:' + k }
                accelator = { keys.entity_team: k }
                base_url = 'https://www.crunchbase.com/organization/' + accelorators_dict[k]
                print 'base url:', base_url
                yield self.cv.goto_url(base_url).addCallback(lambda ign: task.deferLater(reactor, 5, defer.succeed, True))
                print 'loaded complete'
                html = yield self.cv.to_html()
                
                div = html.cssselect('image-with-fields-card image-with-text-card div')[0]
                accelator[keys.entity_pic] = div.cssselect('div.text-card-image.flex-none.cb-image-with-placeholder.organization img')[0].attrib['src']
                print 'pic:', accelator[keys.entity_pic]
                try:
                    accelator[keys.entity_name] = div.cssselect('field-formatter[contexttype="profile"] span.component--field-formatter.field-type-text_short.ng-star-inserted')[0].attrib['title']
                except:                    
                    accelator[keys.entity_name] = div.cssselect('field-formatter[contexttype="profile"] span.component--field-formatter.field-type-text_blob.ng-star-inserted')[0].attrib['title']
                print 'name:', accelator[keys.entity_name]
                accelator[keys.entity_description] = div.cssselect('field-formatter[contexttype="profile"] span.component--field-formatter.field-type-text_long.ng-star-inserted')[0].attrib['title']
                
                for dt in html.cssselect('label-with-info'):
                    try:
                        label = parse.csstext(dt).lower().strip()
                        value = dt.getparent().getnext()
                        label_value = parse.csstext(value).strip()
                        label = ''.join([x for x in label if ord(x) not in [194,160]]) #).replace('?', '')
                        print 'label:', label, 'label value:', label_value
                        if label == 'founded date':
                            accelator[keys.entity_founded] = label_value
                        elif label == 'founders':
                            accelator[keys.entity_founders] = label_value
                        elif label == 'facebook':
                            accelator[keys.entity_facebook] = value.cssselect('a[title="View on Facebook"]')[0].attrib['href'].split('/')[3]
                        elif label == 'linkedin':
                            accelator[keys.entity_linkedin] = value.cssselect('a[title="View on Linkedin"]')[0].attrib['href'].split('/')[4]
                        elif label == 'twitter':
                            accelator[keys.entity_twitter] = value.cssselect('a[title="View on Twitter"]')[0].attrib['href'].split('/')[3]
                        elif label == 'website':
                            accelator[keys.entity_website] = fixed.clean_url(value.cssselect('a')[0].attrib['href'])
                    except:
                        pass 
                for a in html.cssselect('dd.social-links a'):
                    accelator[a.attrib['data-icons']] = a.attrib['href'].split('.com/')[1]
                print 'pause'
                yield task.deferLater(reactor, 10, defer.succeed, True)
                print 'done pause'
                print accelator
                accelator['players'] = []
                yield self.cv.goto_url('https://www.crunchbase.com/organization/' + accelorators_dict[k])                
                accelator_url = 'https://www.crunchbase.com/organization/' + accelorators_dict[k] + '/investments/investments_list'
                print 'accelator url:', accelator_url
                
                
                noi_href = '/search/funding_rounds/field/organizations/num_investments/' + accelorators_dict[k]
                print 'noi href:', noi_href
                
                noi_link = html.cssselect('a.cb-link.component--field-formatter.field-type-integer.ng-star-inserted[href="' + noi_href + '"]')[0]
                
                noi = int(parse.csstext(noi_link).strip().replace(',',''))
                print 'number of investments:', noi
                
                yield self.cv.goto_url(accelator_url).addCallback(lambda ign: task.deferLater(reactor, 10, defer.succeed, True))
                
                investments_html = yield self.cv.to_html()
                current_noi = len(investments_html.cssselect('grid-body div.component--grid-body div.body-wrapper grid-row div.component--grid-row'))
                while current_noi < noi:
                    for x in range(0, 20):
                        QTest.keyClick(app.opengl, Qt.Key_PageDown, Qt.NoModifier, 10)
                    self.cv.page().runJavaScript(show_more_js)
                    yield task.deferLater(reactor, 2, defer.succeed, True)                            
                    investments_html = yield self.cv.to_html()
                    current_noi = len(investments_html.cssselect('grid-body div.component--grid-body div.body-wrapper grid-row div.component--grid-row'))
                    print 'new current_noi:', current_noi
                accelator['players'] = []                
                for i, c in enumerate(investments_html.cssselect('grid-body div.component--grid-body div.body-wrapper grid-row div.component--grid-row')):
                    player = {}
                    try:                    
                        try:
                            player[keys.entity_founded] = parse.csstext(c.cssselect('grid-cell')[0]).strip()
                        except:
                            pass                                            
                        grid = c.cssselect('grid-cell')[1]                        
                        a_link = grid.cssselect('a.cb-link.layout-row.layout-align-start-center.ng-star-inserted[role="link"]')[0]                    
                        player[keys.entity_name] = a_link.attrib['title']                    
                        player[keys.entity_profile] = fixed.clean_url('https://www.crunchbase.com' + a_link.attrib['href'])
                        try:                    
                            player[keys.entity_pic] = grid.cssselect('img')[0].attrib['src'].replace('h_25,w_25','h_120,w_120')
                        except:
                            pass
                        try:                  
                            player[keys.entity_rounds] = parse.csstext(c.cssselect('grid-cell')[3]).split('-')[0].strip()
                        except:
                            pass
                        try:
                            raised = parse.csstext(c.cssselect('grid-cell')[4])
                            if '\xe2\x80\x94' != raised:
                                player[keys.entity_raised] = raised
                            print player
                            accelator['players'].append(player)
                        except:
                            pass
                    except:
                        pass                       
                accelators.append(accelator)                                    
        except Exception as e:
            print 'entities exception:', e
        players = self.teams_to_players(accelators)
        defer.returnValue(players)
        #with open('/home/ubuntu/scewpt/etc/data/startup/accelators.json', 'w') as json_data:
        #    json.dump(accelators, json_data)
        #print [(a[keys.entity_website], len(a['players'])) for a in accelators] 
