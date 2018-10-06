from amazon.sqs import TweetQueue
from amazon.dynamo import User, EntityHistory

from app import keys
from twitter import twitter_keys, auth, tweets

import requests

class StalkUtil(object):
    
    def recover(self, entity):
        if not entity[keys.entity_twitter_id]:
            maybe = twitter_keys.validate_twitter(entity, False)
            if maybe:
                entity.partial_save()
        if entity[keys.entity_twitter_id]:
            print 'twitter id:', entity[keys.entity_twitter_id]
            u = User().get_by_role('me', keys.entity_twitter)
            oauth = auth.get_oauth(u, u, 'Curator Login')
            recover_url = 'https://api.twitter.com/1.1/users/lookup.json?user_id=%s&include_entities=false' % entity[keys.entity_twitter_id]
            print 'recover_url:', recover_url 
            r = requests.get(recover_url, auth=oauth)
            print r.json()
            try:
                entity[keys.entity_twitter] = r.json()[0]['screen_name']
                entity.partial_save()
            except KeyError:
                del entity[keys.entity_twitter]
                del entity[keys.entity_twitter_id]
                entity.partial_save()            
        else:
            print 'could not recover'
            self.lost(entity)
        
    def lost(self, entity):
        tweet_txt = 'Account Lost: https://twitter.com/' + entity[keys.entity_twitter]                        
        differences = { 'twitter__remove' : entity[keys.entity_twitter] }                                
        self.scout_delta(entity, differences, False)            
        tweet = {}
        tweet.update(entity._data)
        tweet[twitter_keys.message_tweet] = tweet_txt
        TweetQueue().createMessage(tweet)            
        del entity[keys.entity_twitter]
        del entity[keys.entity_twitter_id]
        entity.partial_save()    

    def scout_delta(self, item, differences, tweet = True):
        EntityHistory().delta(item, differences)
        if tweet:
            message = {}
            message.update(item._data)
            message.update(differences)
            dt = tweets.delta_tweet(item, item, differences, self.curator, self.league)
            print 'scout delta tweet:', dt
            message[twitter_keys.message_tweet] = dt                     
            TweetQueue().createMessage(message)