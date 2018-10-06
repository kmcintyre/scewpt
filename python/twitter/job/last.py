from amazon.dynamo import Tweet, User
from app import keys, fixed, user_keys

import sys

last_conversation_filter={'known_conversation__null': False}

def last_conversation(l):
    try:
        tweet = [t for t in Tweet().query_2(index=Tweet.index_league, league__eq=l, limit=1, reverse=True, query_filter=last_conversation_filter)][0]
        return tweet._data
    except IndexError:
        pass
    except Exception as e:
        print e.__class__.__name__, e

    
last_retweet_filter={'known_retweet__null': False, 'unknown_retweet__null': False}

def last_retweet(l):
    try:
        tweet = [t for t in Tweet().query_2(index=Tweet.index_league, league__eq=l, limit=1, reverse=True, query_filter=last_retweet_filter, conditional_operator='OR')][0]
        return tweet._data
    except IndexError:
        pass
    except Exception as e:
        print e.__class__.__name__, e

last_tweet_filter={'known_retweet__null': True, 'unknown_retweet__null': True}

def last_tweet(l):
    try:
        tweet = [t for t in Tweet().query_2(index=Tweet.index_league, league__eq=l, limit=1, reverse=True, query_filter=last_tweet_filter)][0]
        return tweet._data
    except IndexError:
        pass
    except Exception as e:
        print e.__class__.__name__, e
        
def get_last_league(site, l, retweet, conversation):
    lt = last_tweet(l)    
    try:             
        print '{:22s} {:15s} {:15s} {:16s} {:20s}'.format(
            site, 
            l, 
            fixed.lingo_since_date(int(lt[Tweet.ts_ms]) / 1000 ), 
            lt[keys.entity_twitter], 
            lt[Tweet.tweet_id]
        )
        if retweet:
            lr = last_retweet(l)
            if lr:
                print '{:23s} {:14s} {:15s} {:16s} {:25s}'.format(
                    '',
                    'retweet', 
                    fixed.lingo_since_date(int(lr[Tweet.ts_ms]) / 1000 ), 
                    lr[keys.entity_twitter], 
                    lr[Tweet.tweet_id]
                )
        if conversation:
            lc = last_conversation(l)
            if lc:
                print '{:23s} {:14s} {:15s} {:16s} {:25s}'.format(
                    '',
                    'conversation', 
                    fixed.lingo_since_date(int(lc[Tweet.ts_ms]) / 1000 ), 
                    lc[keys.entity_twitter], 
                    lc[Tweet.tweet_id]
                )                    
    except:
        locked_league = User().get_by_role(l, keys.entity_twitter)
        locked = False
        if locked_league[user_keys.user_locked]:
            locked = locked_league[user_keys.user_locked]
        print '{:22s} {:15s} {:20s}'.format(
            site, 
            l,
            'unknown-' + str(locked)
        )

def report():
    sls = []    
    for site_leagues_seq in [(u[user_keys.user_role], u[user_keys.user_site_leagues]) for u in User().scan(site_leagues__null=False, inactive__null=True)]:
        sls.append(site_leagues_seq)
    sls = sorted(sls, key=lambda item: item[0])
    for sl_seq in sls:
        #print site_leagues_seq[0], site_leagues_seq[1] 
        sl = sorted(list(sl_seq[1]))
        for league in sl: 
            get_last_league(sl_seq[0], league, len(sys.argv) > 1, len(sys.argv) > 2)

if __name__ == '__main__':
    report()