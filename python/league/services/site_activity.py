from twisted.web.resource import Resource

from twisted.web import server
from twisted.internet import reactor

from league.services import shared
from amazon.dynamo import User
from amazon import instances
from app import keys, user_keys
from twitter import auth

activity_port = 8013

import base64
import hmac
import hashlib
import json
import requests
from urllib import quote_plus

def user_secret_key(u):
    app_key = u[user_keys.user_twitter_apps].keys()[0]
    return str(u[user_keys.user_twitter_apps][app_key][user_keys.user_consumer_secret])

webhook_post_url_fmt = 'https://api.twitter.com/1.1/account_activity/all/env-beta/webhooks.json?url={0}'
webhook_get_url = 'https://api.twitter.com/1.1/account_activity/all/env-beta/webhooks.json'


def verify_webhooks():
    tags = instances.get_instance(requests.get('http://169.254.169.254/latest/meta-data/instance-id').text).tags['Name']
    for tn in tags.split(','):
        tag = tn.strip()
        if tag == 'service':
            print 'verify webhooks:', tag
            me = User().get_by_role('me', keys.entity_twitter)
            oauth = auth.get_oauth(me, me, me[user_keys.user_twitter_apps].keys()[0])
            #r = requests.post(webhook_url_fmt.format(quote_plus('http://service.socialcss.com/activity')), auth=oauth)
            r = requests.get(webhook_get_url, auth=oauth)
            print r.status_code, r.text
        else:
            pass

class ActivityResource(Resource):
    
    isLeaf = True
    consumer_secret_keys = {
        'socialcss.com': user_secret_key(User().get_by_role('me', keys.entity_twitter))
    }
    
    def get_secret_key(self, request):
        print self.consumer_secret_keys, shared.SharedPath().path_site(request)
        if shared.SharedPath().path_site(request) in self.consumer_secret_keys:
            return self.consumer_secret_keys[shared.SharedPath().path_site(request)]
        else:
            ln = request.getRequestHostname().split('.')[0]
            if ln not in self.consumer_secret_keys:
                self.consumer_secret_keys[ln] = user_secret_key(User().get_by_role(ln, keys.entity_twitter))
            return self.consumer_secret_keys[ln]            
    
    def render_POST(self, request):
        shared.SharedPath().response_headers(request, 'application/json')       
        raw_body = request.content.read()
        print 'body:', raw_body, 'headers:', self.requestHeaders.getAllRawHeaders()
        if 'x-twitter-webhooks-signature' in self.requestHeaders.getAllRawHeaders():
            signature = self.requestHeaders.getAllRawHeaders()['x-twitter-webhooks-signature'][7:]
            print 'signature:', signature
            sha256_hash_digest = hmac.new(self.get_secret_key(request), msg=raw_body, digestmod=hashlib.sha256).digest()
            print 'sha256:', sha256_hash_digest 
            if sha256_hash_digest == base64.b64decode(signature):
                print 'valid message'
                body = json.loads(raw_body)
                print 'body:', body
            else:
                print 'invalid message'
        request.write('')
        request.finish()
        return server.NOT_DONE_YET
    
    def render_GET(self, request):
        print 'host:', request.getRequestHostname(), 'request args:', request.args
        shared.SharedPath().response_headers(request, 'application/json')
        if 'crc_token' in request.args:            
            sha256_hash_digest = hmac.new(self.get_secret_key(request), msg=request.args['crc_token'][0], digestmod=hashlib.sha256).digest()
            request.write(json.dumps({
                'response_token': 'sha256=' + base64.b64encode(sha256_hash_digest)
            }))
            request.finish()
        else:
            request.write(json.dumps({
                'host': request.getRequestHostname(),
                'path': request.path,
                'args': request.args
            }))
            request.finish()             
        return server.NOT_DONE_YET

if __name__ == '__main__':
    reactor.callWhenRunning(verify_webhooks)
    reactor.listenTCP(activity_port, server.Site(ActivityResource()))    
    reactor.run()