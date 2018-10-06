import os
os.environ['QTDISPLAY'] = ':2'
from qt import qt5
print 'stalk:', qt5.qt_version

from twitter.qt.browser import TwitterView, TwitterEnginePage
from amazon.dynamo import Entity, ProfileTwitter, User
from twitter import twitter_keys, twitter_helper


from app import keys, fixed, parse, user_keys, time_keys

from twisted.internet import reactor, defer, task

from decimal import Decimal
import sys
import requests
import base64
import time
import datetime
from lxml import etree
from boto.dynamodb2.exceptions import ProvisionedThroughputExceededException

from requests.exceptions import SSLError

universal = User().get_by_role('me', keys.entity_twitter)

class QualifiedException(Exception):
    pass
class BlockedException(Exception):
    pass
class ProtectedException(Exception):
    pass
class LoopException(Exception):
    pass

js_common_fmt="""
    var fykt = document.querySelector('%s');
    var gc = 'div[class="js-stream-item"][role="listitem"]';
    try {        
        var fik = parseInt(fykt.innerHTML.trim().split(' ')[0].replace(',',''));
        var vfik = document.querySelectorAll(gc).length
        if ( vfik < fik ) {
            function hitdown() {
                window.scrollTo(0,document.body.scrollHeight);
                setTimeout(function () {
                    alert('down:' + document.querySelectorAll(gc).length + ' of ' + fik);
                }, 1000);        
            }
            if ( vfik == 18 ) {
                setTimeout(function () { alert('msg: first time'); hitdown(); }, 2000);
            } else {
                hitdown()
            }
        } else {
            alert('good:' + fik);
        }
    } catch (err) {
        alert('good:' + err);
    }
"""

class StalkWebPage(TwitterEnginePage):

    def javaScriptAlert(self, qurl, msg):
        self.view().js_bridge(msg)            
    
    js_selector = 'li[data-element-term="follower_you_know_toggle"] span[aria-hidden="true"]'  

class StalkView(TwitterView):
    
    oauth = None
    
    def rate_limited(self, html):
        drawer = html.cssselect('div[class="alert-messages js-message-drawer-visible"][id="message-drawer"] div.message div.message-inside span.message-text')
        if len(drawer) > 0 and parse.csstext(drawer[0]) == 'Sorry, you are rate limited. Please wait a few moments then try again.':
            print 'rate limited!'
            return True
        return False
            
    def mutual_following(self, mutual_list, entity, profile):
        existing_following = profile[twitter_keys.league_mutual(self.user[user_keys.user_role])]
        if not existing_following:
            print 'no existing following!'
            existing_following = set([])         
        profile[twitter_keys.league_mutual(self.user[user_keys.user_role])] = set(mutual_list)
        try:
            print 'added:', profile[twitter_keys.league_mutual(self.user[user_keys.user_role])] - existing_following, 'removed:', existing_following - profile[twitter_keys.league_mutual(self.user[user_keys.user_role])]             
        except Exception as e:
            print 'print mutual_following exception:', e
        
    def js_bottom(self):
        return js_common_fmt % self.page().js_selector
    
    def js_bridge(self, msg):
        if msg.startswith('good:'):
            print 'good:', msg[5:]
            self.at_bottom.callback(True)
        elif msg.startswith('down:'):
            self.toward_bottom += 1
            if (self.toward_bottom > self.max_down_hits and self.max_down_hits > 0) or self.toward_bottom > 1000:
                self.at_bottom.errback(LoopException())
            print'toward_bottom:', self.toward_bottom, msg, self.max_down_hits
            self.page().runJavaScript(self.js_bottom())
        elif msg.startswith('msg:'):
            print 'js_bridge msg:', msg
        elif msg.startswith('image:'):
            print 'js_bridge image:', msg[:28]
            target = open("/home/ubuntu/Desktop/test.png", 'w')
            target.write(base64.b64decode(msg[28:]))
            target.close()
        elif msg.startswith('error:'):
            print 'js_bridge error:', msg[:6]
        elif msg.startswith('left:'):
            print 'js_bridge set left:', msg[5:]
            self.page().left = msg[5:] 
        elif msg.startswith('top:'):
            print 'js_bridge set top:', msg[4:]
            self.page().top = msg[4:]            
    
    def goto_bottom(self):
        print 'goto_bottom'                      
        self.at_bottom = defer.Deferred()
        self.toward_bottom = 0
        print 'start goto bottom!', self.toward_bottom, self.max_down_hits
        self.js_bridge('down: start!')
        return self.at_bottom
    
    def handle_exception(self, err):
        print 'stalk handle exception', err.value 
        possible = err.trap(BlockedException, ProtectedException, LoopException)
        if possible == BlockedException:
            print 'Blocked'              
        elif possible == ProtectedException:
            print 'Protected'
        elif possible == LoopException:
            print 'Loop Exception'            
        elif hasattr(possible, 'l'):
            print 'should maybe consider not visiting:', possible.l            
                    
    def check_protected(self, html, l):
        if self.protected(html):
            print 'is protected'
            raise ProtectedException()         

    def check_qualified(self, html, l):
        try:
            followers = html.cssselect('div.ProfileUserList.ProfileUserList--socialProof')[0].cssselect('div.ProfileUserList-title span.ProfileUserList-listName a')[0]
            tf = int(parse.csstext(followers).split(' ')[0].replace(',',''))
            self.max_down_hits = 10 + tf / 6
            print 'max down hits:', self.max_down_hits
            return tf
        except IndexError as e:
            print 'check qualified failed to find element'
            self.max_down_hits = 0
            raise QualifiedException()
        except Exception as e:
            print 'check qualified exception:', e
            self.max_down_hits = 0
            raise Exception()
    
    def check_blocked(self, html, l):
        if len(html.cssselect('p.BlocksYouTimeline-explanation a[href="https://support.twitter.com/articles/20172060"]')) > 0:
            print 'am blocked'
            be = BlockedException()
            l[twitter_keys.league_blocks(self.user[user_keys.user_role])] = True
            print 'set league blocked:', l[twitter_keys.league_blocks(self.user[user_keys.user_role])]
            raise be
        elif twitter_keys.league_blocks(self.user[user_keys.user_role]) in l.keys():
            print 'not blocked'
            del l[twitter_keys.league_blocks(self.user[user_keys.user_role])]
             
    def error_stalk(self, err):
        sslerror = err.trap(SSLError)
        if sslerror == SSLError:
            reactor.stop()
        print 'stalk error:', err

    @defer.inlineCallbacks
    def stalk_stats(self, twitter, follow = False):
        print 'tweeter_home_stats:', twitter      
        yield self.goto_url('https://twitter.com/' + twitter)
        yield task.deferLater(reactor, 2, defer.succeed, True)
        html = yield self.to_html()      
        if self.rate_limited(html):
            yield task.deferLater(reactor, 900, defer.succeed, True)            
        if len(html.cssselect('div.ProfileWarningTimeline[data-element-context="fake_account_profile"] button.EdgeButton.EdgeButton--tertiary.ProfileWarningTimeline-button')) > 0:
            print 'unusual exception'
            raise Exception()                
        stats = self.home_twitter(html, twitter, self.user[user_keys.user_role])        
        if follow:
            pt = self.protected(html)                    
            bt = self.blocked(html)
            can_follow = self.can_follow(html, twitter) 
            am_following = self.am_following(html, twitter)                                
            print 'am following:', am_following, 'can follow:', can_follow, 'protected:', pt, 'am blocked:', bt
        defer.returnValue(stats)
    
    @defer.inlineCallbacks
    def stalk_entity(self, ltp):        
        r = requests.get('https://twitter.com/' + ltp[keys.entity_twitter], headers={'User-Agent': 'curl/7.35.0', 'Accept': '*/*'})
        print 'stalk entity:', ltp[keys.entity_twitter], 'status code:', r.status_code
        if r.status_code == 404:
            twitter_util.StalkUtil().recover(ltp)            
        elif '<title>Twitter / Account Suspended</title>' in r.text:
            twitter_util.StalkUtil().lost(ltp)
        else:
            try:
                profile_twitter = None
                while not profile_twitter:
                    try:
                        profile_twitter = ProfileTwitter().profile_last(ltp[keys.entity_twitter_id], None, ltp[time_keys.ts_scout])
                    except ProvisionedThroughputExceededException as e:
                        yield task.deferLater(reactor, 2, defer.succeed, True)            
                stats = yield self.stalk_stats(ltp[keys.entity_twitter], True)            
                profile_twitter._data.update(stats)
                if not profile_twitter['protected'] or profile_twitter['following']:
                    js = """
                    function update() {
                        var sp = document.querySelector('div.ProfileUserList.ProfileUserList--socialProof div.ProfileUserList-heading span.ProfileUserList-listName a');
                        return sp
                    }
                    update().click();                    
                    """
                    self.page().runJavaScript(js)
                    
                    yield task.deferLater(reactor, 2, defer.succeed, True)
                    
                    html = yield self.to_html()
                    self.check_blocked(html, ltp)
                    self.check_protected(html, ltp)
                    mutual_followers = self.check_qualified(html,  ltp)
                    print 'mutual followers:', mutual_followers
                    
                    yield self.goto_bottom()
                    html2 = yield self.to_html()
                    
                    user_ids = []
                    for div in html2.cssselect('div[class="js-stream-item"][role="listitem"]'):
                        user_ids.append(div.attrib['data-item-id'])
                    print 'user ids length:', len(user_ids)
                    if len(user_ids) > 0:
                        self.mutual_following(user_ids, ltp, profile_twitter)
                    else:
                        print 'skipped mutual following'
                    yield task.deferLater(reactor, 3, defer.succeed, True)                        
                else:        
                    print 'protected:', ltp[keys.entity_twitter]
                if profile_twitter.needs_save():
                    profile_twitter.partial_save() 
                ltp[twitter_keys.league_ts_followers(self.user[user_keys.user_role])] = int(time.time())
                ltp.partial_save()
            except BlockedException as e:
                print 'blocked exception!' 
                ltp[twitter_keys.league_ts_followers(self.user[user_keys.user_role])] = int(time.time())
                ltp.partial_save()
            except QualifiedException as e:
                print 'qualified exception'
            except Exception as e:
                print 'stalk entity exception:', e, 'twitter:', ltp[keys.entity_twitter], 'profile:', ltp[keys.entity_profile]                          

    @defer.inlineCallbacks
    def stalk(self):
        try:
            today = datetime.datetime.now()
            day_of_year = (today - datetime.datetime(today.year, 1, 1)).days + 1
            odd_day = day_of_year % 2 == 0
            count = 0;
            qfs = [{'twitter__null': False, 'ts_scout__null': False, 'ts_followers_' + self.user[user_keys.user_role] + '__lt' : twitter_keys.stalk_fresh() }, {'twitter__null': False, 'ts_scout__null': False, 'ts_followers_' + self.user[user_keys.user_role] + '__null' : True }]
            for qf in qfs:
                for ltp in Entity().query_2(league__eq=self.role[1], query_filter = qf, reverse = odd_day):
                    count += 1
                    print 'COUNT:', count, 'twitter:', ltp[keys.entity_twitter], 'league:', ltp[keys.entity_league], 'qualify:', qf
                    yield self.stalk_entity(ltp).addErrback(self.error_stalk) 
            yield task.deferLater(reactor, 10, defer.succeed, True)
            self.hide()        
            self.stalk_done()
            
            mv = TwitterMatchView(fresh=False)
            self.tw_clone(mv)
            mv.setFixedWidth(1024)
            mv.setFixedHeight(768)        
            mv.show()
            yield mv.match()
        except Exception as e:
            print 'stalk exception:', e                          
        reactor.callLater(0, reactor.stop)
                       
    def stalk_done(self):
        print 'stalk_done previous:', fixed.lingo_since(self.user, time_keys.ts_stalked)
        self.user[time_keys.ts_stalked] = int(time.time())
        print 'considered stalked'
        self.user.partial_save()                        
        
    def start(self):        
        self.twitter_initialize()
        print 'called stalk:', self.role[1], fixed.lingo_since(self.user, time_keys.ts_stalked)
        self.signin()

class TwitterMatchView(StalkView):
    
    qf = {'twitter__null': True, 'match_twitter__null': True}
    consider = 0

    def match_error(self, err):
        print 'generic match error:', err
        
    @defer.inlineCallbacks
    def match_entity(self, ltp, force_match=False):
        search = fixed.adjust_name(ltp) + ' twitter'
        try:
            print 'search term:', search
        except:
            pass
        cites = yield self.google(search, results=5, domain='twitter.com')
        possibles = self.match_filter_status(cites)
        try:
            print 'possibles:', possibles, ltp[keys.entity_profile]
        except:
            print 'cannot print possibles'        
        d2 = self.match_possibles(possibles)
        d2.addCallback(self.create_match, ltp)
        d2.addErrback(self.match_error)
        yield d2

    def filter_create(self, metadata):
        return dict((k, v) for k, v in metadata.iteritems() if v)

    def create_match(self, qualified, player):
        if len(qualified):
            now = int(time.time())
            print 'has match:', [q[keys.entity_twitter] for q in qualified]
            matches = [self.filter_create(q) for q in qualified]
            for m in matches:
                m[time_keys.ts_match_twitter] = now 
            player[keys.entity_match_twitter] = matches            
        else:
            print 'no match:', player[keys.entity_profile]
            player[keys.entity_match_twitter] = int(time.time())
        player.partial_save()
        return defer.SUCCESS

    def get_qualifying(self):
        return int(self.user[user_keys.user_twitter_qualify]) if self.user[user_keys.user_twitter_qualify] else 1 

    def match_qualify(self, match_stats, qualified):
        if keys.entity_twitter not in match_stats or self.page().url().toString() == 'https://twitter.com/account/suspended' or match_stats[keys.entity_twitter] in [ems[keys.entity_twitter] for ems in qualified]:            
            return qualified        
         
        fik = 0 if twitter_keys.match_followers_you_know not in match_stats else match_stats[twitter_keys.match_followers_you_know]         
        if fik >= self.get_qualifying() or match_stats[twitter_keys.match_blocked] or match_stats[twitter_keys.match_protected]:
            for et in Entity().query_2(index=Entity.index_twitter_league, twitter__eq=match_stats[keys.entity_twitter]):
                print 'already in league:', et[keys.entity_league]
                if et[keys.entity_league] != 'celebrity' and self.league[keys.entity_league] != 'celebrity':
                    return qualified
            print 'qualified:', match_stats[keys.entity_twitter], 'match that i know:', fik
            qualified.append(match_stats)
        elif match_stats[twitter_keys.match_protected]:
            print '    protected:', 'https://twitter.com/' + match_stats[keys.entity_twitter]
        return qualified

    @defer.inlineCallbacks
    def match_possibles(self, match_possibles):
        qualified = []
        for p in match_possibles:
            try:
                print 'match:', p
            except:
                pass
            d = self.goto_url(p)
            d.addCallback(lambda res: task.deferLater(reactor, 2, defer.succeed, res))
            d.addCallback(self.to_html)
            html = yield d
            if self.rate_limited(html):
                yield task.deferLater(reactor, 900, defer.succeed, True)                       
            stats = self.home_twitter(html)
            self.match_qualify(stats, qualified)
        defer.returnValue(qualified)

    bad_matches = ['/.../', '/status/', '/hashtag/', '/media', '/statuses', '/lists/', '/search?']
    def match_filter_status(self, possibles):
        print 'match filter status:', possibles
        check = []        
        for possible in possibles:
            should_check = True
            for bad in self.bad_matches:        
                    if bad in possible and should_check:
                        print 'possible bad:', possible, bad
                        should_check = False
            if should_check:
                possible_handle = twitter_keys.gettwitter(possible)
                print 'possible_handle:', possible_handle 
                if not possible_handle:
                    should_check = False
                elif possible_handle.lower() in [block.lower() for block in self.blocked]:                      
                    should_check = False
            if should_check:
                check.append(possible)
        return [c.split(' ')[0].split('?')[0] for c in check]

    def match_clean(self):        
        now = int(time.time())
        print 'match loop qualifying twitter:', self.get_qualifying()
        existing = 0
        for clean in Entity().query_2(league__eq=self.role[1], query_filter={'match_twitter__null': False}):
            if isinstance(clean[keys.entity_match_twitter], Decimal):
                if now - clean[keys.entity_match_twitter] > 60 * 60 * 24 * 7:
                    del clean[keys.entity_match_twitter]
                    try:
                        print 'clean:', clean[keys.entity_profile]
                    except:
                        pass
                    clean.partial_save()
            else:
                dirty = False
                for m in clean[keys.entity_match_twitter]:
                    if time_keys.ts_match_twitter not in m or now - m[time_keys.ts_match_twitter] > 60 * 60 * 24 * 14:
                        clean[keys.entity_match_twitter].remove(m)
                        dirty = True
                if dirty:
                    clean.partial_save()
                else:
                    existing += 1
        print 'existing matches:', existing  

    @defer.inlineCallbacks
    def match_loop(self):        
        i = 1
        for ltp in Entity().query_2(league__eq=self.role[1], query_filter = self.qf):
            print 'consider:', i , 'of:', self.consider, ltp[keys.entity_league], ltp[keys.entity_profile]
            yield self.match_entity(ltp)
            i += 1
        self.match_done()                        

    def match(self):
        self.blocked = twitter_keys.get_blocked(self.curator[user_keys.user_role], keys.entity_twitter)         
        print 'blocked twitter:', self.blocked
        self.match_clean()
        self.consider = Entity().query_count(league__eq=self.role[1], query_filter = self.qf)
        print 'match consider:', self.consider 
        d = self.match_loop()
        d.addErrback(self.error_view)                
        return d        

    def match_done(self):
        print 'match loop complete - updating from:', fixed.lingo_since_date(self.user[time_keys.ts_match_twitter])
        self.user[time_keys.ts_match_twitter] = int(time.time())
        self.user.partial_save()


def stalk_report(sl):
    for index, league in enumerate(sl):
        print '{:3s}'.format(str(index+1)), '{:20s}'.format(league[user_keys.user_role]), 'since stalked:', fixed.lingo_since(league, time_keys.ts_stalked)

if __name__ == '__main__':    
    leagues = [l for l in User().get_leagues() if user_keys.user_locked not in l]
    leagues = sorted(leagues, key=lambda item: item[time_keys.ts_stalked])        
    try:        
        try:
            stalk_index = int(sys.argv[1])
            stalk_league = leagues[stalk_index]
        except:
            stalk_league = [l for l in leagues if l[user_keys.user_role] == sys.argv[1]][0]                              
        print 'stalk league:', stalk_league[user_keys.user_role]        
        swp = StalkWebPage()
        sv = StalkView(page=swp)
        sv.setFixedWidth(1024)
        sv.setFixedHeight(768)
        sv.show()
        sv.role = ('stalk', stalk_league[user_keys.user_role])
        reactor.callWhenRunning(sv.start)
        reactor.run()                
    except Exception as e:
        stalk_report(leagues)
