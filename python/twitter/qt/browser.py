import os
#os.environ['QTDISPLAY'] = ':2'
from qt import qt5
print 'browser:', qt5.qt_version
from twitter.auth import TwitterAuth
from amazon.dynamo import ProfileTwitter

from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtCore import QUrl
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from twisted.internet import defer, reactor, task

from app import keys, user_keys, parse, time_keys, fixed

from services import client

from amazon import emails
from amazon.dynamo import Entity, User, UserAvailable

from twitter import twitter_keys

import requests
import time

from qt.view import ChromeView

from lxml import etree

class TwitterEnginePage(QWebEnginePage):
    pass
class MeException(Exception):
    pass

js_email_focus="""
    var ne = document.querySelector('input[id="user_email"][name="user[email]"]');
    ne.value = '';
    ne.focus();
"""

js_email="""
    document.querySelector('button[id="settings_save"][type="submit"]').click()
"""

js_save = """
    document.querySelector('button[id="save_password"][class="btn primary-btn modal-submit"]').click()            
"""

class TwitterSignIn(object):

    tw_signInClick = """
        setTimeout(function () {
            if ( document.querySelector('a.StreamsLogin.js-login') ) {
                document.querySelector('a.StreamsLogin.js-login').click();                
            } else if ( document.querySelector('input.js-submit[type="submit"][value="Log in"]') ) {                
            }         
            setTimeout(function () {
                if ( document.querySelector('input.js-submit[type="submit"][value="Log in"]') ) {
                    document.querySelector('input.js-submit[type="submit"][value="Log in"]').click()
                }
            }, 2000);
            
        }, 1000);        
    """

    tw_signIn = """
        var my_username = '%s';
        var my_password = '%s';
        setTimeout(function () {
            if ( document.querySelector('input.js-username-field.email-input') ) {
                document.querySelector('input.js-username-field.email-input').value=my_username;
                document.querySelector('input.js-password-field[type="password"]').value=my_password;
                if ( document.querySelector('button.submit.EdgeButton') ) {
                    document.querySelector('button.submit.EdgeButton').click();
                } else if ( document.querySelector('a.js-login.EdgeButton') ) {
                    document.querySelector('a.js-login.EdgeButton').click();
                }            
            } else if ( document.querySelector('input.js-signin-email.email-input') ) {
                document.querySelector('input.js-signin-email.email-input').value=my_username;
                document.querySelector('input.text-input[type="password"]').value=my_password;
                document.querySelector('input.submit.EdgeButton[value="Log in"]').click();
            }
        }, 2000);                   
    """

    def reconnect(self, ign = None):
        if hasattr(self, 'custom_finish'):
            self.page().loadFinished.connect(self.custom_finish)
        else:
            self.page().loadFinished.connect(self.finished)

    def execute_role(self, arg = None):
        print 'execute_role:', self.role, 'argument:', arg, 'me:', self.me
        getattr(self, self.role[0])()

    def check_apps(self, html):
        print 'check_apps:', html
    
    def error_login_complete(self, err):
        try:
            possible = err.trap(MeException)
            
            if possible == MeException:
                print 'me exception'
                parse.dumpit(err.value.html, 'me_exception.html')                
                self.user[user_keys.user_locked] = True
                self.user.partial_save()                    
        except Exception as e:
            print 'possible exception:', e
        print 'error_login_complete:', err
        #reactor.stop()
    
    def login_complete(self, okay):
        print 'login complete!', okay,self.page().url().toString()
        self.page().loadFinished.disconnect(self.login_complete)
        self.page().loadFinished.connect(self.finished)                
        d = defer.Deferred()
        d.addCallback(etree.HTML)
        d.addCallback(self.whoami)
        d.addCallback(self.execute_role)
        d.addErrback(self.error_login_complete)        
        self.page().toHtml(d.callback)
        
    def enter_credentials(self, okay):
        print 'enter credentials:', self.page().url().toString()        
        self.page().loadFinished.disconnect(self.enter_credentials)
        self.page().loadFinished.connect(self.login_complete)
        tu = self.user[user_keys.user_username]
        tp = self.user[user_keys.user_password]               
        js = self.tw_signIn % (tu, tp)
        self.page().runJavaScript(js)
        
    def click_login(self, okay):
        #d = self.to_html()
        #d.addCallback(lambda html: parse.dumpit(html, 'login.html'))
        print 'click login:', self.page().url().toString()        
        self.page().loadFinished.disconnect(self.click_login)
        self.page().loadFinished.connect(self.enter_credentials)
        self.page().runJavaScript(self.tw_signInClick)        
        
    def signin(self):
        print 'signin - going reactive!'
        self.page().loadFinished.connect(self.click_login)
        self.page().load(QUrl('https://twitter.com'))

    def prompt_check(self, html):
        if len(html.cssselect('h3[class="PromptbirdPrompt-title"]')) > 0:
            pc = parse.csstext(html.cssselect('h3[class="PromptbirdPrompt-title"]')[0])
            print pc
            print etree.tostring(html.cssselect('h3[class="PromptbirdPrompt-title"]')[0])
            #parse.dumpit(html, 'dumpit_prompt.html')
            print '    PROMPT!'
            #raise Exception('lockout_check:')
        return html
    
    def lockout_check(self, html):
        if len(html.cssselect('h3[class="PromptbirdPrompt-title"]')) > 0:
            print etree.tostring(html.cssselect('h3[class="PromptbirdPrompt-title"]')[0])
            #parse.dumpit(html, 'dumpit_lockout.html')
            print '    LOCKOUT!'
            #raise Exception('lockout_check!')
        return html    
    
    def error_signin(self, err):
        print 'error_signin stopping:', err
        reactor.stop()    

class TwitterStatsView(object):
    
    def protected(self, html):
        return len(html.cssselect(twitter_keys.protected_tweets)) > 0
    
    def can_follow(self, html, twitter):
        cf = 'div[class~="user-actions"][class~="btn-group"][class~="not-following"][class~="not-muting"][data-screen-name="' + twitter + '"]'
        return len(html.cssselect(cf)) > 0

    def blocked(self, html):
        return html.find('.//p[@class="BlocksYouTimeline-explanation"]') is not None    

    def am_following(self, html, twitter):
        is_following = 'div[class~="user-actions"][class~="btn-group"][class~="following"][class~="not-muting"][class~="including"][data-screen-name="' + twitter + '"]'
        return len(html.cssselect(is_following)) > 0    
    
    def home_twitter(self, html, expected = None, league_name = None):
        #print 'home twitter'
        tw = html.cssselect('h2.ProfileHeaderCard-screenname.u-inlineBlock.u-dir')    
        twitter = None
        try:
            twitter = parse.csstext(tw[0])[1:].split(' ')[0]
        except:
            pass
        print '    TWITTER:', twitter, 'expected:', expected
        if not twitter:
            print 'raise missing'
            raise twitter_keys.MissingException()            
        stats = {}        
        
        if expected and expected != twitter:
            mismatch = twitter_keys.MismatchException()
            mismatch.found = twitter
            raise mismatch
        
        if league_name is None:            
            try:
                stats[twitter_keys.match_avatar] = html.cssselect('img.ProfileAvatar-image')[0].attrib['src'].strip()
            except:
                pass
            
            stats[keys.entity_twitter] = twitter
            
            pt = len(html.cssselect(twitter_keys.protected_tweets)) > 0        
            bt = html.find('.//p[@class="BlocksYouTimeline-explanation"]') is not None
            
            stats[twitter_keys.match_protected] = pt
            stats[twitter_keys.match_blocked] = bt            
            try:
                stats[twitter_keys.match_bio] = parse.csstext(html.find('.//div[@class="ProfileHeaderCard"]/p[@class="ProfileHeaderCard-bio u-dir"]'))
            except:
                pass
            try:
                stats[twitter_keys.match_followers] = parse.csstext(html.cssselect('li.ProfileNav-item--followers a span.ProfileNav-value')[0])
                print 'followers:', stats[twitter_keys.match_followers]
            except:
                pass
            try:
                stats[twitter_keys.match_tweets] = parse.csstext(html.cssselect('li.ProfileNav-item--tweets a span.ProfileNav-value')[0])
                print 'tweets:', stats[twitter_keys.match_tweets] 
            except:
                pass
            
            stats[twitter_keys.match_name] = parse.csstext(html.find('.//h1[@class="ProfileHeaderCard-name"]'))
            if stats[twitter_keys.match_protected]:
                stats[twitter_keys.match_name] = stats[twitter_keys.match_name].replace('Protected Tweets','')    
            
            if stats[twitter_keys.match_name].endswith('Protected Tweets'):
                stats[twitter_keys.match_name] = stats[twitter_keys.match_name].replace('Protected Tweets', '')
                stats[twitter_keys.match_protected] = True
                
            stats[twitter_keys.match_verified] = False            
            if 'Verified account' in stats[twitter_keys.match_name]:
                stats[twitter_keys.match_name] = stats[twitter_keys.match_name].replace('Verified account','')
                stats[twitter_keys.match_verified] = True
        else:            
            stats[ProfileTwitter.who_to_follow] = []
            try:
                rec_div = html.find('.//div[@class="WhoToFollow-users js-recommended-followers"]')        
                for rec in rec_div.findall('.//div[@class="js-account-summary account-summary js-actionable-user "]/div[@class="content"]/a/span/span[@class="username u-dir"]/b'):                
                    stats[ProfileTwitter.who_to_follow].append(parse.csstext(rec))
            except:
                pass
            
            stats[ProfileTwitter.who_to_follow_promo] = []
            try:
                for promoted in rec_div.findall('.//a[@class="js-promoted-badge js-user-profile-link"]'):
                    promo = promoted.attrib['href'][1:]       
                    stats[ProfileTwitter.who_to_follow_promo].append(promo)
            except:            
                pass
            
        if html.find('.//p[@class="BlocksYouTimeline-explanation"]') is None:
            try:
                stats[ProfileTwitter.photos_videos] = parse.csstext(html.cssselect('a.PhotoRail-headingWithCount.js-nav')[0]).split(' ')[0]             
            except:
                pass 

            try:
                stats[ProfileTwitter.moments] = parse.csstext(html.cssselect('li.ProfileNav-item--moments a span.ProfileNav-value')[0])
                print 'moments:', stats[ProfileTwitter.moments] 
            except:
                pass                
                            
            try:
                vl = parse.csstext(html.find('.//div[@class="ProfileHeaderCard-vineProfile "]/span[@class="ProfileHeaderCard-vineProfileText u-dir"]/a')[0])
                if vl is not None:
                    stats[ProfileTwitter.vineloops] = vl
                    stats[ProfileTwitter.vine] = html.find('//div[@class="ProfileHeaderCard-vineProfile "]/span[@class="ProfileHeaderCard-vineProfileText u-dir"]/a')[0].attrib['href']
            except:
                pass
    
            try:
                fyf = html.cssselect('a[href="/' + twitter + '/followers_you_follow"]')
                if len(fyf) > 0:
                    kf = int(parse.csstext(fyf[0]).split(' ')[0])
                    print 'known followers:', kf
                    if league_name:
                        stats[twitter_keys.league_followers_you_know(league_name)] = kf 
                    else:
                        stats[twitter_keys.match_followers_you_know] = kf                    
                else:                
                    print 'no known followers!'
                    if league_name:
                        stats[twitter_keys.league_followers_you_know(league_name)] = 0
                    else:
                        stats[twitter_keys.match_followers_you_know] = 0
            except Exception as e:
                print 'known followers exception:', e                                                               
        return stats
    

class TwitterView(ChromeView, TwitterSignIn, TwitterAuth, TwitterStatsView):    
    
    whoami_renew = True
    
    def league_initialize(self):
        try:          
            self.league = Entity().get_item(league=self.role[1], profile='league:' + self.role[1])
            print 'league initialize complete:', self.league[keys.entity_league]
        except Exception as e:
            print 'league initialize exception:', e    
    
    def twitter_initialize(self, available = False):        
        self.available = available
        print 'twitter initialize:', self.role[1], 'available:', self.available        
        try:
            if available:
                self.user = UserAvailable().get_by_role(self.role[1], keys.entity_twitter)
            else:
                self.user = User().get_by_role(self.role[1], keys.entity_twitter)
            print 'twitter initialiaze user:', self.user[user_keys.user_role], self.user[user_keys.user_username], self.user[user_keys.user_password]
        except Exception as e:
            print 'twitter initialize user exception:', e            
        try:            
            self.curator = User().get_curator(self.role[1])
            print 'twitter initialize curator:', self.curator[user_keys.user_role]
        except Exception as e:
            print 'twitter initialize curator exception:', e
        self.league_initialize()    
    
    def tw_clone(self, window):
        window.me = self.me
        window.role = self.role
        window.user = self.user
        try:
            window.curator = self.curator
        except Exception as e:
            print 'clone curator exception', e
        try:            
            window.league = self.league
        except Exception as e:
            print 'clone league exception', e        
      
    def status_twitter(self, check_url):
        print 'check_url:', check_url 
        check = requests.head(check_url, headers={'User-Agent': 'curl/7.35.0', 'Accept': '*/*'}, verify=False)                
        print 'twitter plus response:', check_url, check.status_code
        return check    

    @defer.inlineCallbacks
    def notifications(self):
        yield self.goto_url('https://twitter.com/i/notifications')
        yield task.deferLater(reactor, 30, defer.succeed, True)
        reactor.callLater(0, reactor.stop)

    @defer.inlineCallbacks    
    def developer(self):
        yield self.goto_url('https://developer.twitter.com')

    @defer.inlineCallbacks    
    def apps(self):
        yield self.goto_url('https://apps.twitter.com')
        try:            
            html = yield self.to_html()
            #parse.dumpit(html, 'apps.html')
            for h2 in html.cssselect('div[class="app-details"] h2'):
                a = h2.cssselect('a')[0]
                appname = parse.csstext(a)
                print 'appname:', appname
                if not self.user[user_keys.user_twitter_apps]:
                    self.user[user_keys.user_twitter_apps] = { appname: {} }
                    self.user[user_keys.user_twitter_auth] = { appname: {} }
                    yield self.goto_url('https://apps.twitter.com/' + a.attrib['href'].replace('show', 'keys'))
                    html2 = yield self.to_html()
                    #parse.dumpit(html2, 'apps2.html')
                    for span in html2.cssselect('div[class="app-settings"] div[class="row"] span[class="heading"]'):
                        if parse.csstext(span) == 'Consumer Key (API Key)':
                            self.user[user_keys.user_twitter_apps][appname][user_keys.user_consumer_key] = parse.csstext(span.getnext())
                        if parse.csstext(span) == 'Consumer Secret (API Secret)':
                            self.user[user_keys.user_twitter_apps][appname][user_keys.user_consumer_secret] = parse.csstext(span.getnext())
                    for span in html2.cssselect('div[class="access"] div[class="row"] span[class="heading"]'):
                        if parse.csstext(span) == 'Access Token':
                            self.user[user_keys.user_twitter_auth][appname][user_keys.user_auth_token] = parse.csstext(span.getnext())
                        if parse.csstext(span) == 'Access Token Secret':
                            self.user[user_keys.user_twitter_auth][appname][user_keys.user_auth_token_secret] = parse.csstext(span.getnext())
                    self.user.partial_save()
        except Exception as e:
            print 'apps exception:', e                    
    
    @defer.inlineCallbacks    
    def update_email(self):
        if 'mail.ru' not in self.user[user_keys.user_username]:            
            return 
        yield self.goto_url('https://twitter.com/settings/account')
        try:
            new_email = ''.join([c for c in self.user[user_keys.user_username].lower() if not c.isdigit()])
            print 'new_email:', new_email
            new_email = new_email.split('@')[0] + '@socialcss.com'
            print 'new_email:', new_email
            
            md = {'filter': {'derived_to': new_email}}
            d = client.mail_listener(mail_domain='mail.scewpt.com', message_filter_dic=md)
            d.addCallback(client.hearing_back, new_email)
            d.addErrback(self.error_view)                    
                    
            self.page().runJavaScript(js_email_focus)        
            yield task.deferLater(reactor, 1, defer.succeed, True)
            QTest.keyClicks(qt5.app.opengl, new_email, Qt.NoModifier, 20)
            
            yield task.deferLater(reactor, 2, defer.succeed, True)
            self.page().runJavaScript(js_email)
            
            yield task.deferLater(reactor, 2, defer.succeed, True)
            
            QTest.keyClicks(qt5.app.opengl, self.user[user_keys.user_password], Qt.NoModifier, 20)
            yield task.deferLater(reactor, 2, defer.succeed, True)
            
            self.page().runJavaScript(js_save)
            
            result = yield d            
            print 'result:', result['file_dest']
            email_html = etree.HTML(emails.get_html_from_msg(result['file_dest']))
            print 'email_html:', email_html
            for el in email_html.cssselect('a[href]'):
                if etree.tostring(el, method="text", encoding='UTF-8').lower().strip() == 'confirm now':
                    yield self.goto_url(el.attrib['href'])
                    new_user = {}
                    new_user.update(self.user._data)
                    self.user.delete() 
                    new_user[user_keys.user_username] = new_email
                    if self.available:
                        UserAvailable().put_item(data=new_user)
                    else:
                        User().put_item(data=new_user)
        except Exception as e:
            print 'update email exception:', e 
    
    @defer.inlineCallbacks    
    def update_available(self):
        yield self.authorize()
        yield self.update_email()     
    
    @defer.inlineCallbacks    
    def authorize(self):
        print 'authorize:', self.role[1]
        univeral = User().get_by_role('me', keys.entity_twitter)
        try:
            for univeral_app in univeral[user_keys.user_twitter_apps].keys():
                if self.user[user_keys.user_twitter_auth] and univeral_app in self.user[user_keys.user_twitter_auth]:
                    print univeral_app, 'authorization:', self.user[user_keys.user_twitter_auth][univeral_app]
                else:            
                    univeral_ans = yield self.create_token(univeral, univeral_app, True)
                    print univeral_app, 'token ans:', univeral_ans                 
        except Exception as e:            
            print 'authorize universal exception:', e
        try:
            if self.curator[user_keys.user_twitter_apps]:
                for curator_app in self.curator[user_keys.user_twitter_apps].keys():                
                    if self.user[user_keys.user_twitter_auth] and curator_app in self.user[user_keys.user_twitter_auth]:
                        print curator_app, 'authorization:', self.user[user_keys.user_twitter_auth][curator_app]
                    else:            
                        curator_ans = yield self.create_token(self.curator, curator_app)
                        print curator_app, 'token ans:', curator_ans            
        except Exception as e:            
            print 'authorize curator exception:', e

    @defer.inlineCallbacks
    def myself(self):
        print 'myself:', self.role[1]
        if self.role[1] == 'me':
            for t in [User]:
                for user in t().scan(type__eq=keys.entity_twitter):
                    if user[keys.entity_twitter]:
                        try:
                            d = defer.Deferred()
                            self.deferred_cbs.append(d)                            
                            visit_function = """(function () {{ document.location='{}'; return true }})();""".format('https://twitter.com/' + user[keys.entity_twitter])
                            self.page().runJavaScript(visit_function)
                            yield d
                            yield task.deferLater(reactor, 3, defer.succeed, True)
                            html = yield self.to_html()
                            if self.can_follow(html, user[keys.entity_twitter]) and not self.am_following(html, user[keys.entity_twitter]):
                                print 'following:', user[keys.entity_twitter]
                                do_follow = twitter_keys.do_follow_fmt % user[keys.entity_twitter]
                                self.page().runJavaScript('document.querySelector(\'' + do_follow + '\').click()')
                                yield task.deferLater(reactor, 30, defer.succeed, True)
                        except Exception as e:
                            print 'myself exception:', e
        if self.role[1].endswith('.com'):
            for user in User().get_leagues(self.role[1]):
                if user[keys.entity_twitter]:
                    try:
                        d = defer.Deferred()
                        self.deferred_cbs.append(d)                            
                        visit_function = """(function () {{ document.location='{}'; return true }})();""".format('https://twitter.com/' + user[keys.entity_twitter])
                        self.page().runJavaScript(visit_function)
                        yield d
                        yield task.deferLater(reactor, 3, defer.succeed, True)
                        html = yield self.to_html()
                        if self.can_follow(html, user[keys.entity_twitter]) and not self.am_following(html, user[keys.entity_twitter]):
                            do_follow = twitter_keys.do_follow_fmt % user[keys.entity_twitter]
                            self.page().runJavaScript('document.querySelector(\'' + do_follow + '\').click()')
                            yield task.deferLater(reactor, 60, defer.succeed, True)                        
                    except Exception as e:
                        print 'myself:', e                

    def browser(self):
        print 'browser:', self.role[1]
        
    def suspended(self):
        self.goto_url("https://support.twitter.com/forms/general?subtopic=suspended")
    
    def whoami(self, html):
        #parse.dumpit(html, 'test.html')
        try:
            self.me = html.cssselect('a.DashboardProfileCard-screennameLink.u-linkComplex.u-linkClean')[0].attrib['href'][1:]
        except IndexError:
            e = MeException()
            e.html = html
            raise e
        print 'ME:', self.me
        if self.me != self.user[keys.entity_twitter]:
            print 'unknown me:', self.me, self.user[keys.entity_twitter]            
            if self.whoami_renew or keys.entity_twitter not in self.user:
                self.user[keys.entity_twitter] = self.me                                
                self.user.partial_save()
                print 'update me:', self.me, self.user._data
            else:
                print 'not renewing:', self.me, self.user[keys.entity_twitter]
                raise Exception('No Renewing')
        else:
            if len(html.cssselect('div[class="Banner-textContent"][id="account-suspended"]')) == 0:
                print 'known me:', self.me, self.user[keys.entity_twitter]
                if self.user[user_keys.user_locked]:
                    del self.user[user_keys.user_locked]
                    self.user.partial_save()
                self.user[time_keys.ts_last_login] = int(time.time())
                self.user.partial_save()
                print self.user[time_keys.ts_last_login]
                try:
                    self.league[time_keys.ts_last_login] = int(time.time())
                    self.league.partial_save()
                except Exception as e:
                    print 'could not save login:', e
            else:
                e = MeException()
                e.html = html
                raise e                
        return html
    
if __name__ == '__main__':
    import sys
    tw = TwitterView() 
    role = 'browser'
    if len(sys.argv) > 2:
        role = sys.argv[2]
    try:
        tw.role = (role, sys.argv[1])
        user_available = False
        if len(sys.argv) > 3:
            user_available = True
        tw.setFixedWidth(1024)
        tw.setFixedHeight(768) 
        tw.show()    
        tw.twitter_initialize(user_available)
        tw.signin()
        reactor.run()
    except Exception as e:
        print 'missing league argument'
        for curator in sorted([c for c in User().get_curators()], key = lambda k: k[time_keys.ts_last_login]):
            print 'curator:', curator[user_keys.user_role], fixed.lingo_since_date(curator[time_keys.ts_last_login])            
        users = User().get_leagues(None, keys.entity_twitter)
        users.sort(key = lambda k: k[time_keys.ts_last_login])
        print 'users:', len(users)
        for league in users:
            print 'league:', league[user_keys.user_role], fixed.lingo_since_date(league[time_keys.ts_last_login])    
