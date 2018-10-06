from amazon.dynamo import Entity
from league import league_shared, keys_market
from app import keys, fixed, parse

from twisted.web.client import getPage
from twisted.internet import reactor, defer, task
import requests

from lxml import html, etree
import json
import time

class InterceptorBuilder(object):
    from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor

    class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
        
        block = False
        
        def interceptRequest(self, info):
            #print info.requestUrl().toString()
            if self.block and ('cnn.com' not in info.requestUrl().toString() and 'turner.com' not in info.requestUrl().toString()):
                info.block(True)
                print 'blocked:', info.requestUrl().toString()
            elif 'fb.me' in info.requestUrl().toString() or 'brandcdn.com' in info.requestUrl().toString() or 'nbcudigitaladops.com' in info.requestUrl().toString() or 'widget.perfectmarket.com' in info.requestUrl().toString():
                info.block(True)
                print 'blocked:', info.requestUrl().toString()
                        
    
    intercept = WebEngineUrlRequestInterceptor()

def get_symbol_profile(symbol):
    url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/' + symbol + '?formatted=true&lang=en-US&region=US&modules=assetProfile' 
    return getPage(str(url)).addCallback(json.loads)

def get_symbol_price(symbol):
    url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/' + symbol + '?formatted=true&lang=en-US&region=US&modules=financialData'    
    return getPage(str(url)).addCallback(json.loads)

@defer.inlineCallbacks
def get_quote_price(company):
    try:
        js = yield get_symbol_price(company[keys_market.symbol].upper())
        company[keys.entity_price] = js['quoteSummary']['result'][0]['financialData']['currentPrice']['fmt']
    except:
        pass
    
def get_market_realtime_quote(js):     
    return js['quoteSummary']['result'][0]['financialData']['currentPrice']['fmt']
    
@defer.inlineCallbacks
def get_sector_industry(company):
    try:
        js = yield get_symbol_profile(company[keys_market.symbol].upper())
        ap = js['quoteSummary']['result'][0]['assetProfile']        
        company[keys.entity_industry] = ap['industry']
        company[keys.entity_sector] = ap['sector']
        company[keys.entity_website] = ap['website']
    except:
        pass
    
class CEO(league_shared.Common):

    @defer.inlineCallbacks
    def ceo_linkedin(self, ceos):
        print 'ceos length:', len(ceos)
        for ceo in ceos:
            print ceo
            try:
                st = ceo[keys.entity_name] + ' of ' + ceo[keys.entity_company] + ' site:linkedin.com'
                d = self.cv.bing(search_term=st, results=1, domain='www.linkedin.com')
                d.addErrback(self.error_league)
                results = yield d
                print 'bing results:', results[0]
                ceo[keys.entity_match_linkedin] = fixed.clean_url(results[0])
            except Exception as e:
                print e
        defer.returnValue(ceos)

    @defer.inlineCallbacks
    def key_execs(self):
        execs = []
        for e in Entity().query_2(league__eq='market', profile__beginswith='http://finance.yahoo.com/quote/'):
            if 'profile' not in e[keys.entity_profile]:
                ceo = {}
                ceo[keys.entity_profile] = fixed.clean_url(e[keys.entity_profile] + '/profile')                
                try:
                    js = yield get_symbol_profile(e[keys_market.symbol])
                    officer = js['quoteSummary']['result'][0]['assetProfile']['companyOfficers'][0]#['companyOfficers'][0]
                    ceo[keys.entity_name] = officer['name'].split(',')[0]
                    for suffix in ['CPCU', 'CFP', 'B.S. Petroleum Engineering', 'B.Sc.', 'D.Phil.', 'B.S. Pharm', 'M.B.B.S', 'BSC', '(Biochemistry)', 'M.S.', 'Esq.', 'MBBS', 'M.B.A.','(Petroleum Engineering)', 'CFA', 'AC', 'M.P.P.M.', 'J.D.','FCAS', 'CPA', 'MBA', 'M.D.', 'Ph.D.', 'BA', 'P.E.', 'Sc.D.','FCMAA', 'M.B. Ch. B.']:
                        ceo[keys.entity_name] = ceo[keys.entity_name].replace(suffix, '')
                    if ceo[keys.entity_name].startswith('Mr.') or ceo[keys.entity_name].startswith('Dr.') or ceo[keys.entity_name].startswith('Ms.'):
                        ceo[keys.entity_name] = ceo[keys.entity_name].split(' ', 1)[1]
                    ceo[keys.entity_name] = ceo[keys.entity_name].replace('  ', ' ').strip()
                    try:
                        ceo[keys.entity_age] = officer['age']
                    except:
                        pass
                    ceo[keys.entity_position] = officer['title'].split(',')[0]
                    try:
                        if officer['totalPay']['fmt']:
                            ceo[keys.entity_salary] = officer['totalPay']['fmt']
                    except:
                        pass
                    execs.append(ceo)
                    print ceo[keys.entity_name]
                except Exception as e:
                    print 'ceo exception:', e
        defer.returnValue(execs)         

    def entities(self):
        return self.key_execs()
    
class CNBC(league_shared.Common):    
    
    @defer.inlineCallbacks
    def components(self, doc):
        companies = []
        for table in doc.cssselect('div.flex_chart table.data.quoteTable'):
            trs = table.cssselect('tr')[1:]
            print 'components length:', len(trs)
            for tr in trs:            
                try:
                    company = {}
                    company[keys.entity_index] = self.stock_index
                    company[keys.entity_name] = parse.csstext(tr.cssselect('td[data-field="name"]')[0]).strip()
                    company[keys.entity_name] = company[keys.entity_name].replace(' Inc','').replace(' Corp','').replace(' Ltd','').replace(' PLC', '').strip()
                    
                    company[keys.entity_price] = parse.csstext(tr.cssselect('td[data-field="last"]')[0]).strip()                    
                    company[keys_market.symbol] = parse.csstext(tr.cssselect('td[data-field="symbol"] a')[0]).strip()
                    company[keys.entity_profile] = fixed.clean_url('http://finance.yahoo.com/quote/' + company[keys_market.symbol].upper())
                    yield get_sector_industry(company)
                    companies.append(company)
                except Exception as e:
                    print 'nasday exception:', e
        defer.returnValue(companies)
        
    def companies(self):
        d = self.cv.goto_url(self.component_url).addCallback(lambda ign: task.deferLater(reactor, 10, defer.succeed, True)).addCallback(self.cv.to_html)
        d.addCallback(self.components)
        d.addErrback(self.error_league)
        return d            

    def entities(self):
        d = self.companies()
        d.addErrback(self.error_league)
        return d

class DOW(CNBC):

    component_url = 'http://www.cnbc.com/dow-components/'    
    stock_index = 'DOW'

class NASDAQ(CNBC):

    component_url = 'http://www.cnbc.com/nasdaq-100/'
    stock_index = 'NASDAQ 100'    
    
class SANDP(league_shared.Common):
    
    list_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'    
        
    @defer.inlineCallbacks
    def components(self, doc):
        print ''
        companies = []
        #/html/body/div[3]/div[3]/div[4]/div/table[1]
        #n = doc.xpath('/html/body/div[3]/div[4]/div[4]/table[1]')[0]
        table = doc.cssselect('h2 span[id^="S.26P_500_Component_Stocks"]')[0].getparent().getnext()
        trs = table.cssselect('tr')[1:]
        print 'table:', table, len(trs)
        for tr in trs:
            print 'tds:', len(tr)            
            if len(tr) == 9:
                symbol_name = tr[0][0].text.replace('-', '.')
                print 'symbol name:', symbol_name 
                try:
                    company = {}
                    company[keys.entity_index] = 'S&P 500'
                    company[keys_market.symbol] = tr[0][0].text
                    company[keys.entity_name] = tr[1][0].text
                    company[keys.entity_filings] = tr[2][0].attrib['href']
                    yield get_sector_industry(company)
                    yield get_quote_price(company)
                    company[keys.entity_profile] = fixed.clean_url('http://finance.yahoo.com/quote/' + company[keys_market.symbol].upper())
                    if tr[6].text:
                        company['firstadded'] = tr[6].text
                    print company
                    companies.append(company)
                    print 'sandp 500:', company[keys_market.symbol]
                except:
                    print 'component additional exception:', symbol_name
        defer.returnValue([c for c in companies if keys_market.symbol in c])

    def companies(self):
        d = self.cv.goto_url(SANDP.list_url).addCallback(self.cv.to_html)
        d.addCallback(self.components)
        d.addErrback(self.error_league)     
        return d

    def entities(self):
        return self.companies()

class RUSSELL(league_shared.SharedLeague):
    
    russell_url = 'http://money.cnn.com/data/markets/russell/?page='
    #suffixes = ['', '?s=RUT&row=250', '?s=RUT&row=500', '?s=RUT&row=750', '?s=RUT&row=1000', '?s=RUT&row=1250', '?s=RUT&row=1500', '?s=RUT&row=1750', '?s=RUT&row=2000']
    
    @defer.inlineCallbacks
    def companies(self):
        companies = []
        #for x in range(1,25):
        for x in range(1,97):
            try:
                rurl = RUSSELL.russell_url + str(x)
                print 'rurl:', rurl
                html = yield self.cv.goto_url(rurl).addCallback(self.cv.to_html)
                for a in html.cssselect('a.wsod_symbol'):
                    company = {}
                    company[keys.entity_index] = 'Russell 2000'
                    company[keys_market.symbol] = a.attrib['href'].rsplit('?symb=', 1)[1]
                    #company[keys.entity_name] = ' '.join([w.lower().capitalize() for w in parse.csstext(tds[1]).split(' ')])
                    #if company[keys.entity_name].split(' ')[0].lower() == 'Inc.':
                    #    cn = company[keys.entity_name].split(' ')[1:]
                    #    cn.append('Inc.')
                    #    company[keys.entity_name] = ' '.join(cn)
                    #print company
                    yield get_sector_industry(company)
                    yield get_quote_price(company)                    
                    company[keys.entity_profile] = fixed.clean_url('http://finance.yahoo.com/quote/' + company[keys_market.symbol].upper())
                    companies.append(company)
            except Exception as e:
                print 'company exception:', e
        for c in companies:
            try:
                html2 = yield getPage(c[keys.entity_profile]).addCallback(etree.HTML)
                entity_name = parse.csstext(html2.cssselect('title')[0])
                entity_name = entity_name.split('Summary for ', 1)[1]
                entity_name = entity_name.split(' - Yahoo Finance')[0]
                if entity_name.endswith(','):
                    entity_name = entity_name[:-1]
                if 'Co. Co' in entity_name:
                    entity_name = entity_name.replace('Co. Co', 'Co')
                c[keys.entity_name] = entity_name
                print c[keys.entity_name], c[keys.entity_profile]
            except Exception as e:
                print e
        defer.returnValue([c for c in companies if keys.entity_name in c and keys.entity_profile in c])        

    def entities(self):
        return self.companies()


class MARKET(league_shared.SharedLeague):
    
    min_size = 3500
    max_size = 4000
    
    
    @defer.inlineCallbacks
    def company_profile(self, companies):
        print 'company_profile:', len(companies)
        for c in companies:
            ticker_url = 'http://finance.yahoo.com/quote/' + c['symbol'] + '/profile'
            try:
                print 'ticker:', ticker_url
                doc = yield self.cv.goto_url(ticker_url).addCallback(self.cv.to_html).addErrback(self.error_market) 
                try:
                    c[keys.entity_website] = fixed.clean_url(doc.xpath('//td[@class="yfnc_modtitlew1"]/*[@href]')[1].text)
                except Exception as e:
                    print 'no website', c['symbol']
            except Exception as e:
                print 'key_exec exception:', e, ticker_url
        defer.returnValue([c for c in companies if keys.entity_profile in c])

    def get_quote(self, symbol):
        import xmlrpclib
        print 'get_quote:', symbol
        proxy = xmlrpclib.ServerProxy('http://quote.ventorta.com/quote')
        result = proxy.retrieve_quote(symbol)
        return result
        
    def filter_tweet(self, msg):
        time.sleep(3)
        key_changes = [k for k in msg.keys() if '__' in k]
        if len(key_changes) == 1 and key_changes[0] == 'price__change':
            return True
        return False
    
    @defer.inlineCallbacks    
    def entities(self):
        market = []
        d = DOW()
        d.cv = self.cv
        dow = yield d.entities()
        print 'dow:', len(dow)
        market.extend(dow)
        
        n = NASDAQ()
        n.cv = self.cv
        nasdaq = yield n.entities()
        print 'nasdaq:', len(nasdaq)
        market.extend([n for n in nasdaq if n[keys.entity_profile] not in [m[keys.entity_profile] for m in market]])
        s = SANDP()
        s.cv = self.cv
        sandp = yield s.entities()
        print 'S&P 500:', len(sandp)
        market.extend([s for s in sandp if s[keys.entity_profile] not in [m[keys.entity_profile] for m in market]])
        ib = InterceptorBuilder()        
        ib.intercept.block = True
        r = RUSSELL()
        self.cv.page().profile().setRequestInterceptor(ib.intercept)
        r.cv = self.cv
        russell = yield r.entities()
        print 'Russell 2000:', len(russell)
        market.extend([r for r in russell if r[keys.entity_profile] not in [m[keys.entity_profile] for m in market]])
        
        ib.intercept.block = False
        ceo = yield CEO().entities()
        print 'ceo:', len(ceo)
        market.extend(ceo)
        defer.returnValue(market)       
        
    def prune(self):
        from amazon.sqs import TweetQueue
        tq = TweetQueue('market')
        while True:
            m = tq.getMessage()
            if not m:
                exit()    
            msg = json.loads(m.get_body())
            if 'price__change' in msg:
                a = float(msg['price__change'].split('__')[0])
                b = float(msg['price__change'].split('__')[1])
                c = max(a, b)
                d = min(a, b)
                pd = 100 * (c - d)/c
                print 'percentage difference:', pd, msg['symbol']
                if pd < 3:
                    tq.deleteMessage(m)