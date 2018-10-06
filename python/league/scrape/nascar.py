from league import league_shared
from app import keys, fixed, parse
from twisted.internet import defer

class XFINITY(league_shared.Common):

    def xfinity_drivers(self, html):
        drivers = []
        for driver_tr in html.cssselect('table.driver-list-table tr')[1:]:
            player = {}
            
            team = parse.csstext(driver_tr.cssselect('td.driver-team-td')[0])
            if not team:
                team = NASCAR.unaffiliated
            player[keys.entity_team] = team

            try:    
                player[keys.entity_carlogo] = driver_tr.cssselect('td.driver-make-td img')[0].attrib['src']
                try:
                    make_style = player[keys.entity_carlogo].lower()
                    if 'ford' in make_style:
                        player[keys.entity_carmake] = 'Ford'
                    elif 'toyota' in make_style:
                        player[keys.entity_carmake] = 'Toyota' 
                    elif 'chevrolet' in make_style:
                        player[keys.entity_carmake] = 'Chevrolet'
                except:
                    print 'no carmake'                
            except:
                print 'no carlogo'                

            try:
                player[keys.entity_carnumber] = parse.csstext(driver_tr.cssselect('td.driver-team-td')[0])
            except:
                print 'no car number'
            
            driver_el = driver_tr.cssselect('td.driver-name-td a')[0]
            
            player[keys.entity_profile] = fixed.clean_url(NASCAR.nascar_url + driver_el.attrib['href'])
            player[keys.entity_name] = parse.csstext(driver_el)

            player[keys.entity_circuit] = self.get_common_name()
                         
            drivers.append(player)
        return drivers

    def entities(self):        
        d = self.cv.goto_url(NASCAR.nascar_url + '/drivers/xfinity-series')
        #d = self.cv.goto_url(NASCAR.nascar_url + '/en_us/drivers.xfinity-series.html')
        d.addCallback(self.cv.to_html)
        d.addCallback(self.xfinity_drivers)
        d.addErrback(self.error_league)
        return d

class TRUCK(league_shared.Common):
    
    def truck_drivers(self, html):
        drivers = []
        for driver_art in html.cssselect('a[class="driverDetailLink"]'):
            driver_art.getparent().getparent()
            driver = {}
            driver[keys.entity_name] = parse.csstext(driver_art)
            driver[keys.entity_profile] = fixed.clean_url(NASCAR.nascar_url + driver_art.attrib['href'])

            tr = driver_art.getparent().getparent().getparent().getparent().getparent()

            driver[keys.entity_rank] = parse.csstext(tr.cssselect('th')[0])
            
            driver[keys.entity_carnumber] = parse.csstext(tr.cssselect('td')[2])
            driver[keys.entity_points] = parse.csstext(tr.cssselect('td')[3])
            driver[keys.entity_points_behind] = parse.csstext(tr.cssselect('td')[4]).replace('--','')
            driver[keys.entity_starts] = parse.csstext(tr.cssselect('td')[5])
            driver[keys.entity_wins] = parse.csstext(tr.cssselect('td')[6])
            driver[keys.entity_top5] = parse.csstext(tr.cssselect('td')[7])
            driver[keys.entity_top10] = parse.csstext(tr.cssselect('td')[8])
            driver[keys.entity_dnf] = parse.csstext(tr.cssselect('td')[9])        

            team = parse.csstext(driver_art.getparent().getprevious())
            if not team or team.lower() == 'tbd' or 'java.lang.string' in team.lower():
                team = NASCAR.unaffiliated
            elif 'team:' + team not in [t[keys.entity_profile] for t in drivers]:
                drivers.append({ keys.entity_profile: 'team:' + team })
            driver[keys.entity_team] = team
            driver[keys.entity_circuit] = self.get_common_name() 
            drivers.append(driver)
        return drivers

    def entities(self):
        d = self.cv.goto_url(NASCAR.nascar_url + '/en_us/camping-world-truck-series/standings.html')
        d.addCallback(self.cv.to_html)
        d.addCallback(self.truck_drivers)
        d.addErrback(self.error_league)
        return d

class SPRINTCUP(league_shared.Common):

    def sprintcup_drivers(self, html):
        drivers = []
        for tr in html.cssselect('table.driver-list-table tr')[1:]:
            '''
            <tr>
                <td class="driver-name-td"><a href="/drivers/driversaj-allmendinger/">Allmendinger, AJ</a></td>
                <td class="driver-number-td">47</td>
                <td class="driver-make-td"><img src="/wp-content/uploads/sites/7/2017/01/Chevy-Driver-Page-New-2-160x811-265x180.png"></td>
                <td class="driver-team-td">JTG Daugherty Racing</td>
    
            </tr>
            '''
            driver = {}
            driver[keys.entity_profile] = fixed.clean_url(NASCAR.nascar_url + tr.cssselect('td.driver-name-td a')[0].attrib['href'])            
            driver[keys.entity_name] = parse.csstext(tr.cssselect('td.driver-name-td a')[0]).strip()
            driver[keys.entity_name] = driver[keys.entity_name].split(',')[1].strip() + ' ' + driver[keys.entity_name].split(',')[0].strip()
            
            driver[keys.entity_carnumber] = parse.csstext(tr.cssselect('td.driver-number-td')[0])
            team = parse.csstext(tr.cssselect('td.driver-team-td')[0]).strip()
            if not team:
                team = NASCAR.unaffiliated
            driver[keys.entity_team] = team
                            
            driver[keys.entity_carnumber] = parse.csstext(tr.cssselect('td.driver-number-td')[0])
            driver[keys.entity_circuit] = self.get_common_name()
            print driver
            drivers.append(driver)
            #driver[keys.entity_rank] = parse.csstext(div.cssselect('div.position')[0]).strip()
            #driver[keys.entity_name] = parse.csstext(div.cssselect('div.driver div.driver-first')[0]).split() + ' ' + parse.csstext(div.cssselect('div.driver div.driver-last')[0]).split() 
            
            
            #<div class="driver"><div class="driver-first"> Martin</div><div class="driver-last">Truex Jr.</div><div class="legend-symbols"></div></div>
            
            

            #tr = driver_art.getparent().getparent().getparent().getparent().getparent()

            
            #driver[keys.entity_points] = parse.csstext(tr.cssselect('td')[3])
            #driver[keys.entity_points_behind] = parse.csstext(tr.cssselect('td')[4]).replace('--','')
            #driver[keys.entity_starts] = parse.csstext(tr.cssselect('td')[5])
            #driver[keys.entity_wins] = parse.csstext(tr.cssselect('td')[6])
            #driver[keys.entity_top5] = parse.csstext(tr.cssselect('td')[7])
            #driver[keys.entity_top10] = parse.csstext(tr.cssselect('td')[8])
            #driver[keys.entity_dnf] = parse.csstext(tr.cssselect('td')[9])

            
            #if not team:
            #    team = NASCAR.unaffiliated
            #elif 'team:' + team not in [t[keys.entity_profile] for t in drivers]:
            #    drivers.append({ keys.entity_profile: 'team:' + team })                

            driver[keys.entity_circuit] = self.get_common_name()
            drivers.append(driver)
        return drivers

    def entities(self):
        d = self.cv.goto_url(NASCAR.nascar_url + '/drivers/monster-energy-nascar-cup-series/').addCallback(self.cv.to_html)
        d.addCallback(self.sprintcup_drivers)
        d.addErrback(self.error_league)
        return d


class MOTOCROSS(league_shared.Common):
    
    moto_base_url = 'http://www.promotocross.com'

    def moto_drivers(self, html):
        drivers = []
        for h3 in html.cssselect('h3'):
            if 'Class Points' in parse.csstext(h3):
                motoclass = parse.csstext(h3).rsplit(' ', 1)[0]
                print motoclass
                for li in h3.getparent().getnext().cssselect('ol li'):
                    driver = {}
                    fi = li.cssselect('div.field-items')
                    suffix = fi[0].cssselect('a')[0].attrib['href']
                    if suffix.startswith('//'):
                        suffix = suffix[1:]
                    driver[keys.entity_class] = motoclass
                    driver[keys.entity_profile] = fixed.clean_url(self.moto_base_url + suffix)
                    driver[keys.entity_name] = parse.csstext(fi[0])
                    driver[keys.entity_points] = parse.csstext(fi[1])
                    drivers.append(driver)            
        return drivers

    def entities(self):
        d = self.cv.goto_url(self.moto_base_url + '/mx/series-points/2016')
        d.addCallback(lambda ign: self.cv.to_html())
        d.addCallback(self.moto_drivers)
        d.addErrback(self.error_league)
        return d

class F1(league_shared.Common):
    
    def f1_drivers(self, html):
        drivers = []
        for tr in html.cssselect('table.standing-table__table')[0].cssselect('tr')[1:]:
            driver = {}
            driver[keys.entity_rank] = parse.csstext(tr[0])
            anchor = tr[1].cssselect('a')[0]
            driver[keys.entity_name] = parse.csstext(anchor)
            driver[keys.entity_profile] = fixed.clean_url('http://www.skysports.com' + anchor.attrib['href'])            
            driver[keys.entity_nationality] = parse.csstext(tr[2])
            driver[keys.entity_team] = parse.csstext(tr[3])
            if 'team:' + driver[keys.entity_team] not in [t[keys.entity_profile] for t in drivers]:
                drivers.append({ keys.entity_profile: 'team:' + driver[keys.entity_team] })                
            driver[keys.entity_points] = parse.csstext(tr[4])
            drivers.append(driver)
        return drivers

    def entities(self):
        d = self.cv.goto_url('http://www.skysports.com/f1/standings')
        d.addCallback(lambda ign: self.cv.to_html())
        d.addCallback(self.f1_drivers)
        d.addErrback(self.error_league)
        return d

class NASCAR(league_shared.SharedLeague):

    min_size = 300
    max_size = 450
        
    nascar_url = 'http://www.nascar.com'
    unaffiliated = 'Unaffiliated'
    
    @defer.inlineCallbacks    
    def entities(self):
        drivers = []        
        
        s = SPRINTCUP()
        s.cv = self.cv
        
        sc = yield s.entities()
        print 'sprintcup:', len(sc)
        drivers.extend(sc)
        '''
        x = XFINITY()
        x.cv = self.cv
         
        xf = yield x.entities()
        print 'xfinity:', len(xf)
        drivers.extend(xf)        
        
        t = TRUCK()
        t.cv = self.cv
        tr = yield t.entities()    
        print 'truck:', len(tr)    
        drivers.extend(tr)

        m = MOTOCROSS()
        m.cv = self.cv
        mc = yield m.entities()
        print 'motocross:', len(mc)
        drivers.extend(mc)
        
        f = F1()
        f.cv = self.cv
        
        f1 = yield f.entities()
        print 'f1:', len(f1)
        drivers.extend(f1)
        '''
        defer.returnValue(drivers)    
