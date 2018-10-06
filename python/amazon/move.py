from amazon.dynamo import GenericTable, User
from twitter import auth, restful, twitter_keys
from app import user_keys, keys
import pprint
from twitter.twitter_helper import TwitterLeague

class SocialBeta(GenericTable):
    
    table_name = 'social_beta'


print keys._keys_entity
sb = [s for s in SocialBeta().scan(limit = 1)][0]
pprint.pprint(sb._data)

tweets_list = []

if sb['social_act'] == 'retweet':
    tweets_list.append(sb['tweet_retweet_id'])
else:
    tweets_list.append(sb['tweet_id'])
    
universal = User().get_by_role('me', keys.entity_twitter)
oauth = auth.get_oauth(universal, universal, universal[user_keys.user_twitter_apps].keys()[0])
tweets = restful.get_tweets(oauth, tweets_list)
for tweet in tweets:
    tl = TwitterLeague(sb[keys.entity_league])
    tweet[twitter_keys.timestamp_ms] = str(sb['social_ts_received'] * 1000)
    nt = tl.process_tweet(tweet)
    print 'keys:', nt.keys()
    for key in nt.keys():
        if key.encode('utf8') in keys._keys_entity:
            print 'shared key:', key
        else:
            print 'not shared key:', key
