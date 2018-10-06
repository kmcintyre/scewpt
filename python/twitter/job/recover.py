from app import keys
from amazon.dynamo import Entity, Tweet
from amazon.sqs import RecoverQueue

import simplejson as json
import requests
import sys
from twitter import twitter_keys, twitter_util

def do_recover(recover):
    url = 'https://twitter.com/statuses/' + recover[Tweet.tweet_id]
    print 'url:', url
    check = requests.head(url, headers={'User-Agent': 'curl/7.35.0', 'Accept': '*/*'})        
    print 'twitter plus response:', check.status_code, 'url:', url
    if check.status_code == 301:
        redirect = check.headers['Location']
        print 'redirect:', redirect          
        new_twitter = twitter_keys.gettwitter(redirect)         
        entity = Entity().get_item(league=recover[keys.entity_league], profile=recover[keys.entity_profile])
        print 'new twitter:', new_twitter, 'league:', recover[keys.entity_league], 'profile:', recover[keys.entity_profile], 'existing twitter:', entity[keys.entity_twitter]
        if entity[keys.entity_twitter] != new_twitter:
            entity[keys.entity_twitter] = new_twitter
            if twitter_keys.validate_twitter(entity):
                entity.partial_save()
                print 'save new twitter!'
        else:
            print 'twitter already updated'
        

def check_recover_queue():
    rq = RecoverQueue()
    print 'check recover queue:', rq    
    try:
        while True:
            
            msg = rq.getMessage()
            if msg:
                recover = json.loads(msg.get_body())
                print 'recover msg:', recover[keys.entity_twitter_id]
                for r in Tweet().query_2(_twitter_id__eq = recover[keys.entity_twitter_id], limit=1, reverse= True):
                    print 'got last tweet:'
                    do_recover(r)
                print 'delete recover msg!'
                rq.deleteMessage(msg)
            else:
                break
                        
    except Exception as e:            
        print 'recover exception:', e
    exit()
            
if __name__ == '__main__':
    if len(sys.argv) == 1:
        check_recover_queue()
    else:
        for i, r in enumerate([e for e in Entity().query_2(index=Entity.index_twitter_league,twitter__eq=sys.argv[1])]):
            if i == 0:
                twitter_util.StalkUtil().recover(r)
            else:
                twitter_util.StalkUtil().lost(r)
            
        