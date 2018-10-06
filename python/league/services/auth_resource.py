from twisted.web import resource, server
from twisted.web.resource import NoResource
 
from league.services import shared
from amazon.dynamo import Entity, User

from app import keys, fixed, user_keys

from league.services import shared

import json

from requests_oauthlib import OAuth1Session

def auth():    
    twitter = OAuth1Session('client_key',
                            client_secret='client_secret',
                            resource_owner_key='resource_owner_key',
                            resource_owner_secret='resource_owner_secret')

def step1(request):
    request_token_url = 'https://api.twitter.com/oauth/request_token'
    site = shared.SharedPath().path_site(request)
    curator = User().get_by_role(site, keys.entity_twitter)
    app_name = curator[user_keys.user_twitter_apps].keys()[0]
    client_key = curator[user_keys.user_twitter_apps][app_name][user_keys.user_consumer_key]
    client_secret = curator[user_keys.user_twitter_apps][app_name][user_keys.user_consumer_secret]
    oauth = OAuth1Session(client_key, client_secret=client_secret)
    fetch_response = oauth.fetch_request_token(request_token_url)
    #{
    #    "oauth_token": "Z6eEdO8MOmk394WozF5oKyuAv855l4Mlqo7hhlSLik",
    #    "oauth_token_secret": "Kd75W4OQfb2oJTV0vzGzeXftVAwgMnEK9MumzYcM"
    #}
    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')
    print 'oauth_callback_confirmed:', fetch_response.get('oauth_callback_confirmed')

    #oauth = OAuth1(client_key, client_secret=client_secret)
    #r = requests.post(url=request_token_url, auth=oauth)
    #r.content
    #"oauth_token=Z6eEdO8MOmk394WozF5oKyuAv855l4Mlqo7hhlSLik&oauth_token_secret=Kd75W4OQfb2oJTV0vzGzeXftVAwgMnEK9MumzYcM"
    #from urlparse import parse_qs
    #credentials = parse_qs(r.content)
    #resource_owner_key = credentials.get('oauth_token')[0]
    #resource_owner_secret = credentials.get('oauth_token_secret')[0]    
    #oauth = OAuth1Session(client_key, client_secret=client_secret)
    request.write(json.dumps({'oauth_token': resource_owner_key}))
    #request.redirect("https://api.twitter.com/oauth/authorize?oauth_token=" + resource_owner_key)
    request.finish()
    


def error(err, request):
    print 'error:', err, request
    return NoResource()

class AuthResource(resource.Resource):

    isLeaf = True
    
    def tweeters(self, request):
        args = shared.hassocial(request, social_key = keys.entity_twitter, is_null = False)
        print args
        return [p for p in Entity().query_2(**args)]

    def render_GET(self, request):
        shared.SharedPath().response_headers(request, 'application/json')
        print 'tweeters get:', request.uri
        step1(request)
        return server.NOT_DONE_YET
        #shared.SharedPath().response_headers(request, 'application/json')
                        
        #entities = self.tweeters(request)

        #treated_matches = shared.treat(entities)
        #treated_json = json.dumps(treated_matches,cls=fixed.SetEncoder)            
        #request.write('')         
        #request.finish()
        #return server.NOT_DONE_YET