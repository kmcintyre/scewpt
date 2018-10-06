from app import keys, fixed

from amazon.dynamo import EntityHistory, Tweet, User, Entity
from amazon.sqs import TweetQueue
from twitter import auth

from twitter import twitter_keys, tweets 

from league import keys_market

import json
from urlparse import urlparse

import pprint
import requests

from boto.dynamodb2.exceptions import ConditionalCheckFailedException

class TwitterLeague(object):
    
    def __init__(self, league_name):
        self.league = league_name
        self.running = False
        self.store = False
        self.ws = None
        self.league_user = User().get_by_role(self.league, keys.entity_twitter)        
                                        
    def store_tweet(self, tweet):
        if not Tweet().put_item(data=tweet):
            print 'bad:', tweet
            exit(-1)        

    def clean_up(self, cu):
        for k in ['twitter_id', 'ts_drop_prevented', 'ts_followers', 'ts_non_qualified', 'source_instagram', 'source_twitter']:
            for k2 in [k3 for k3 in cu.keys() if k3.startswith(k)]:
                del cu[k2]        

    def clean_tweet(self, tweet):
        if isinstance(tweet, (int, list, float)):
            return
        for k in tweet.keys():
            if not tweet[k] or k.endswith('_str') or k in twitter_keys.filterable_keys:
                if k != twitter_keys.id_str:
                    del tweet[k]
            elif isinstance(tweet[k], dict):
                self.clean_tweet(tweet[k])
            elif isinstance(tweet[k], list):
                [self.clean_tweet(sb) for sb in tweet[k]]
            if k in tweet and not tweet[k]:
                del tweet[k]
                    
    def process_friends(self, tweet):
        print 'friends:', len(tweet[twitter_keys.friends])
    
    def process_delete(self, tweet):
        self.clean_tweet(tweet)
        print 'delete:', tweet
        
    def process_event(self, tweet):
        self.clean_tweet(tweet)
        print 'event:', tweet
                                                  
    def get_entities_urls(self, tweet):
        if twitter_keys.entities in tweet:
            if twitter_keys.urls in tweet[twitter_keys.entities]:
                eu = [u[twitter_keys.expanded_url] for u in tweet[twitter_keys.entities][twitter_keys.urls]]
                if eu:                        
                    return eu
        
    def check_entities(self, tweet):
        if twitter_keys.entities in tweet:
            if twitter_keys.user_mentions in tweet[twitter_keys.entities]:
                mentions_checked = set([])
                for mention in tweet[twitter_keys.entities][twitter_keys.user_mentions]:
                    if mention[twitter_keys.screen_name] != tweet[twitter_keys.user][twitter_keys.screen_name]:              
                        if mention[twitter_keys.screen_name] not in mentions_checked:
                            print 'check:', mention[twitter_keys.screen_name], mention
                            mentions_checked.add(mention[twitter_keys.screen_name])
                            for e3 in Entity().query_2(index=Entity.index_twitter_league, twitter__eq=mention[twitter_keys.screen_name]):
                                print 'know mention:', e3[keys.entity_twitter], e3[keys.entity_league]
                                if Tweet.known_mentions not in tweet:
                                    tweet[Tweet.known_mentions] = []
                                from_league = {Tweet.tweet_user_id: mention[twitter_keys.id_str]}
                                from_league.update(e3._data)
                                self.clean_up(from_league)
                                tweet[Tweet.known_mentions].append(from_league)
            if self.get_entities_urls(tweet):
                print 'urls:', self.get_entities_urls(tweet)
                
    def check_extended_entities(self, tweet):
            if twitter_keys.extended_entities in tweet:
                print 'extended_entities:', tweet[twitter_keys.extended_entities]
                #if twitter_keys.media in tweet[twitter_keys.extended_entities]:
                #    print tweet[twitter_keys.extended_entities][twitter_keys.media]
                #    print [em[twitter_keys.expanded_url] for em in tweet[twitter_keys.extended_entities][twitter_keys.media]]            

    def get_quotee(self, tweet):
        if twitter_keys.quoted_status in tweet:
            print 'quoted_status:', 'https://twitter.com/'+ tweet[twitter_keys.quoted_status][twitter_keys.user][twitter_keys.screen_name] + '/status/' + str(tweet[twitter_keys.quoted_status][twitter_keys.id_str])
            for e2 in Entity().query_2(index=Entity.index_twitter_league, twitter__eq=tweet[twitter_keys.quoted_status][twitter_keys.user][twitter_keys.screen_name]):
                print 'know quotee:', e2[keys.entity_twitter], e2[keys.entity_league]
                return e2       

    def get_retweet(self, tweet):
        if twitter_keys.retweeted_status in tweet:
            print 'retweet_status:', 'https://twitter.com/'+ tweet[twitter_keys.retweeted_status][twitter_keys.user][twitter_keys.screen_name] + '/status/' + str(tweet[twitter_keys.retweeted_status][twitter_keys.id_str])
            for e2 in Entity().query_2(index=Entity.index_twitter_league, twitter__eq=tweet[twitter_keys.retweeted_status][twitter_keys.user][twitter_keys.screen_name]):
                print 'know retweet:', e2[keys.entity_twitter], e2[keys.entity_league]
                return e2
            
    def get_instagrams(self, tweet):
        if self.get_entities_urls(tweet):
            instagrams = [mi for mi in self.get_entities_urls(tweet) if urlparse(mi).netloc  == 'www.instagram.com']
            if instagrams:
                return instagrams
                 
    def get_conversation(self, tweet):
        if twitter_keys.in_reply_to_screen_name in tweet:
            try:
                conversation_entity = [e for e in Entity().query_2(index=Entity.index_twitter_league, twitter__eq=tweet[twitter_keys.in_reply_to_screen_name], league__eq=self.league)][0]
                print 'conversion:', tweet[twitter_keys.in_reply_to_screen_name]#, tweet[twitter_keys.in_reply_to_status_id]
                return conversation_entity
            except:
                pass
        
    def process_status(self, tweet):
        nt = {}
        if self.get_instagrams(tweet):
            print 'instagrams:', self.get_instagrams(tweet)
            nt[Tweet.instagrams] = self.get_instagrams(tweet)
        if twitter_keys.in_reply_to_screen_name in tweet:
            conversation = self.get_conversation(tweet)
            if conversation:
                if twitter_keys.user in tweet and tweet[twitter_keys.in_reply_to_screen_name] == tweet[twitter_keys.user][twitter_keys.screen_name]:
                    nt[Tweet.is_monologue] = True
                else:  
                    nt[Tweet.known_conversation] = { 
                        Tweet.tweet_user_id: tweet[twitter_keys.in_reply_to_user_id]                         
                    }
                    try:
                        nt[Tweet.known_conversation][Tweet.tweet_id] = tweet[twitter_keys.in_reply_to_status_id]
                    except:
                        print 'missing:', twitter_keys.in_reply_to_status_id                        
                    nt[Tweet.known_conversation].update(conversation._data)                
                    self.clean_up(nt[Tweet.known_conversation])
        if twitter_keys.retweeted_status in tweet:
            retweetee = self.get_retweet(tweet)
            if retweetee:
                nt[Tweet.known_retweet] = {
                    Tweet.tweet_user_id: tweet[twitter_keys.retweeted_status][twitter_keys.user][twitter_keys.id_str], 
                    Tweet.tweet_id: tweet[twitter_keys.retweeted_status][twitter_keys.id_str]
                }
                nt[Tweet.known_retweet].update(retweetee._data)                
                self.clean_up(nt[Tweet.known_retweet])
            elif twitter_keys.retweeted_status in tweet:            
                nt[Tweet.unknown_retweet] = {
                    Tweet.tweet_user_id: tweet[twitter_keys.retweeted_status][twitter_keys.user][twitter_keys.id_str], 
                    Tweet.tweet_id: tweet[twitter_keys.retweeted_status][twitter_keys.id_str]                    
                }
        if twitter_keys.quoted_status in tweet:
            quotee = self.get_quotee(tweet)
            if quotee:
                nt[Tweet.known_quote] = {
                    Tweet.tweet_user_id: tweet[twitter_keys.quoted_status][twitter_keys.user][twitter_keys.id_str], 
                    Tweet.tweet_id: tweet[twitter_keys.quoted_status][twitter_keys.id_str]
                }
                nt[Tweet.known_quote].update(quotee._data)                
                self.clean_up(nt[Tweet.known_quote])
            else:
                nt[Tweet.unknown_quote] = {
                    Tweet.tweet_user_id: tweet[twitter_keys.quoted_status][twitter_keys.user][twitter_keys.id_str], 
                    Tweet.tweet_id: tweet[twitter_keys.quoted_status][twitter_keys.id_str]
                }                
        return nt   
                                         
                   
    def process_tweet(self, tweet, return_on_missing_entity = True):
        if tweet[twitter_keys.user][twitter_keys.screen_name] == self.league_user[keys.entity_twitter]:
            print ''
            print 'is me'
            print ''
            return     
                
        try:
            #print 'tweet:', tweet.keys()
            self.clean_tweet(tweet)
            print ''
            try:
                league_entity = [e for e in Entity().query_2(index=Entity.index_twitter_league, twitter__eq=tweet[twitter_keys.user][twitter_keys.screen_name], league__eq=self.league)][0]
            except Exception as e:
                if return_on_missing_entity:
                    return
                league_entity = {'_data': {}}
            tweet_type = 'tweet' if twitter_keys.retweeted_status not in tweet else 'retweet'
            print '    ', tweet_type, 
            if tweet_type == 'tweet':
                print 'https://twitter.com/' + tweet[twitter_keys.user][twitter_keys.screen_name] + '/status/' + str(tweet['id'])
            else:
                print 'https://twitter.com/' + tweet[twitter_keys.user][twitter_keys.screen_name] + '/with_replies'
            nt = { 
                Tweet.tweet_user_id: tweet[twitter_keys.user][twitter_keys.id_str],
                Tweet.tweet_id: tweet[twitter_keys.id_str],                
            }
            try:
                nt[Tweet.ts_ms] = tweet[twitter_keys.timestamp_ms]
            except:
                pass
            nt.update(league_entity._data)
            self.check_entities(tweet)
            self.clean_up(nt)
            status_nt = self.process_status(tweet)
            if status_nt: 
                nt.update(status_nt)
            if Tweet.known_mentions in tweet:
                for mention in tweet[Tweet.known_mentions]:
                    print 'do mention:', mention
                    for k in [Tweet.known_conversation, Tweet.known_quote, Tweet.known_retweet]:
                        if k in nt:
                            print 'check:', nt[k][keys.entity_league], nt[k][Tweet.tweet_user_id], mention[keys.entity_league], mention[Tweet.tweet_user_id] 
                            if str(mention[Tweet.tweet_user_id]) == str(nt[k][Tweet.tweet_user_id]) and mention[keys.entity_league] == nt[k][keys.entity_league]:
                                print 'remove:', mention
                                try:
                                    tweet[Tweet.known_mentions].remove(mention)
                                except Exception as e:
                                    print 'mention already removed:', e
                if tweet[Tweet.known_mentions]:
                    nt[Tweet.known_mentions] = tweet[Tweet.known_mentions]
                    print 'setting mentions:', nt[Tweet.known_mentions]
            self.tweet_augment(nt)
            pprint.pprint(nt)
            if self.store:
                self.store_tweet(nt)
            if self.running:
                self.ws.send(json.dumps(nt, cls=fixed.SetEncoder))                            
            self.check_extended_entities(tweet)            
            tweet.update(nt)
            return nt            
        except ConditionalCheckFailedException:
            print 'failed to write'
        except Exception as e:
            print 'process exception:', e
            print ''
            #pprint.pprint(tweet)
            exit(-1)
    def tweet_augment(self, tweet):
        if self.league == 'market' and keys_market.symbol in tweet:
            url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/' + tweet[keys_market.symbol] + '?formatted=true&lang=en-US&region=US&modules=financialData'
            price = requests.get(url).json()['quoteSummary']['result'][0]['financialData']['currentPrice']['fmt']
            print 'tweet augment price:', price
            tweet[keys_market.price] = price
        elif  self.league == 'crypto' and keys_market.symbol in tweet:
            api = 'https://api.coinmarketcap.com/v1/ticker/{}/'.format(tweet[keys.entity_profile].split('/')[-1])
            crypto_data = requests.get(api).json()[0]
            price = crypto_data['price_usd']
            print 'price:', price
            tweet[keys_market.price] = price
            tweet[keys.entity_rank] = crypto_data['rank']

def delete_sets_and_lists(obj):
    compare_data = {}
    compare_data.update(obj)
    for sk in [k for k in compare_data.keys() if isinstance(compare_data[k], set) or isinstance(compare_data[k], list)]:
        del compare_data[sk]
    return compare_data