from app import user_keys, parse

from amazon.dynamo import User

from twisted.internet import defer

import requests
from requests_oauthlib import OAuth1

from urlparse import parse_qs

def get_oauth(app_user, app_owner, app_name):
    
    CONSUMER_KEY = app_owner[user_keys.user_twitter_apps][app_name][user_keys.user_consumer_key]
    CONSUMER_SECRET = app_owner[user_keys.user_twitter_apps][app_name][user_keys.user_consumer_secret]    
    return OAuth1(
            CONSUMER_KEY,
            client_secret=CONSUMER_SECRET,
            resource_owner_key=app_user[user_keys.user_twitter_auth][app_name][user_keys.user_auth_token],
            resource_owner_secret=app_user[user_keys.user_twitter_auth][app_name][user_keys.user_auth_token_secret]
            )
    
def user_app(user):
    if user[user_keys.user_twitter_auth]:
        for k in user[user_keys.user_twitter_auth]:
            if user_keys.user_read_only not in user[user_keys.user_twitter_auth][k]:
                if user[user_keys.user_twitter_apps] and k in user[user_keys.user_twitter_apps]:
                    return user
                else:
                    curator = User().get_curator(user[user_keys.user_role])
                    if curator[user_keys.user_twitter_apps] and k in curator[user_keys.user_twitter_apps]:
                        return curator    


class TwitterAuth(object):
        
    REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
    AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize?oauth_token="
    ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"

    
    authorize_js = """
        document.querySelector('input[type="submit"][value="Authorize app"]').click()
    """        
    
    @defer.inlineCallbacks
    def create_token(self, app_user, app_name, read_only = False):
        CONSUMER_KEY = app_user[user_keys.user_twitter_apps][app_name][user_keys.user_consumer_key]
        CONSUMER_SECRET = app_user[user_keys.user_twitter_apps][app_name][user_keys.user_consumer_secret]
        
        oauth = OAuth1(CONSUMER_KEY, client_secret=CONSUMER_SECRET)
        r = requests.post(url=self.REQUEST_TOKEN_URL, auth=oauth)
        credentials = parse_qs(r.content)
        resource_owner_key = credentials.get('oauth_token')[0]
        resource_owner_secret = credentials.get('oauth_token_secret')[0]
        
        authorize_url = self.AUTHORIZE_URL + resource_owner_key
        
        html = yield self.goto_url(authorize_url).addCallback(self.to_html)
        
        #parse.dumpit(html, 'authorize.html')
        
        d = defer.Deferred()
        d.addCallback(self.to_html)
        
        self.deferred_cbs.append(d)
        self.page().runJavaScript(self.authorize_js)
        
        html2 = yield d
        #parse.dumpit(html2, 'authorize2.html')
        
        code = parse.csstext(html2.cssselect('kbd code')[0])
        
        oauth = OAuth1(CONSUMER_KEY,
                   client_secret=CONSUMER_SECRET,
                   resource_owner_key=resource_owner_key,
                   resource_owner_secret=resource_owner_secret,
                   verifier=code)
        
        r = requests.post(url=self.ACCESS_TOKEN_URL, auth=oauth)
        credentials = parse_qs(r.content)
        token = credentials.get('oauth_token')[0]
        secret = credentials.get('oauth_token_secret')[0]
        
        print 'app_name:', app_name, 'token:', token, 'secret:', secret

        if not self.user[user_keys.user_twitter_auth]: 
            self.user[user_keys.user_twitter_auth] = {}
        self.user[user_keys.user_twitter_auth][app_name] = { user_keys.user_auth_token: token, user_keys.user_auth_token_secret: secret}
        if read_only:
            self.user[user_keys.user_twitter_auth][app_name][user_keys.user_read_only] = True
        print 'create auth map:', self.user[user_keys.user_twitter_auth]
        self.user.partial_save()
