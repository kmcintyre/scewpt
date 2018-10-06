import re
import json
import time
from app import keys

def stalk_fresh():
    return int(time.time()) - 60 * 60 * 24 * 3.5

filterable_keys = ['source', 'filter_level', 'sizes', 'indices']

tweet_id = 'tweet_id'
tweet_retweet_id = 'tweet_retweet_id'
screen_name = 'screen_name'
display_text_range = 'display_text_range'

in_reply_to_status_id = 'in_reply_to_status_id'
in_reply_to_screen_name = 'in_reply_to_screen_name'
in_reply_to_user_id = 'in_reply_to_user_id'

possibly_sensitive = 'possibly_sensitive'
lang = 'lang'
created_at = 'created_at'
text = 'text'

timestamp_ms = 'timestamp_ms'

entities = 'entities' 
extended_entities = 'extended_entities'
media = 'media'
expanded_url = 'expanded_url'

user = 'user'
urls = 'urls'
from_leagues = 'from_leagues'
user_mentions = 'user_mentions'

friends = 'friends'
id_str = 'id_str'

retweeted_status = 'retweeted_status'
quoted_status = 'quoted_status'

message_list = 'message_list'
message_tweet = 'message_tweet' 
message_pic = 'message_pic'

media_twitter = 'media_twitter'
media_tag_twitter = 'media_tag_twitter'
media_tag_user_id = 'media_tag_user_id'
media_tag_name = 'media_tag_name'

tweeter_following_avatar = 'tweeter_following_avatar'
tweeter_following_bgcolor = 'tweeter_following_bgcolor'
tweeter_following_bgimage = 'tweeter_following_bgimage'
tweeter_following_bio = 'tweeter_following_bio'
tweeter_following_cardhash = 'tweeter_following_cardhash'

match_followers_you_know = 'followers_you_know'
match_protected = 'protected'
match_blocked = 'blocked'
match_verified = 'verified'
match_bio = 'bio'
match_followers = 'followers'
match_tweets = 'tweets'
match_name = 'name'
match_avatar = 'avatar'
match_posts = 'posts'

protected_tweets = 'div[class="ProtectedTimeline"] h2[class="ProtectedTimeline-heading"]'
do_follow_fmt = 'div[data-screen-name="%s"] span.user-actions-follow-button.js-follow-btn.follow-button button.EdgeButton.EdgeButton--secondary.EdgeButton--medium.button-text.follow-text'

def numTwitter(tn):
    if not tn:
        return '0'
    elif tn / 1000000 >= 1000:
        return '' + str(tn / 1000000000) + '.' + str((tn % 1000000000) / 10000000) + 'B'
    elif tn / 1000000 >= 1:
        return '' + str(tn / 1000000) + '.' + str((tn % 1000000) / 10000) + 'M'
    elif tn / 1000 >= 100:
        return '' + str(tn / 1000) + 'K'
    elif tn / 1000 >= 10:
        return '' + str(tn / 1000) + 'K'
    elif tn / 1000 >= 1:
        return '' + str(tn / 1000) + ',' + str(tn % 1000)
    else:
        return '' + str(tn)

def league_mutual(league_name):
    return league_name + '_mutual'

def league_follows(league_name):
    return league_name + '_follows'

def league_blocks(league_name):
    return league_name + '_blocks'

def league_followers_you_know(league_name):
    return league_name + '_followers_you_know'

def league_ts_followers(league_name):
    return 'ts_followers_' + league_name

def gettwitter(url):
    handle = re.search('^https?://(www\.)?twitter\.com/(#!/)?([^/]+)(/\w+)*$', url)
    if handle is not None:
        return handle.group(3).split('?')[0]
    return None

def bio_hash(entity, league):
    from amazon.dynamo import Entity, ProfileTwitter
    tweet = []    
    try:
        es = ProfileTwitter().profile_recent(entity[keys.entity_twitter_id])        
        for ht in re.findall(r"#(\w+)", es[ProfileTwitter.description]):
            add_hash = '#' + ht
            if not ht.isdigit() and add_hash not in tweet:
                tweet.append(add_hash)
    except:
        pass        
    try:
        te = Entity().get_item(league=league[keys.entity_league], profile='team:' + entity[keys.entity_team])
        ts = ProfileTwitter().profile_recent(te[keys.entity_twitter_id])
        for ht in re.findall(r"#(\w+)", ts[ProfileTwitter.description]):
            add_hash = '#' + ht
            if not ht.isdigit() and add_hash not in tweet:
                tweet.append(add_hash)
    except:
        pass
    
    try:
        ls = ProfileTwitter().profile_recent(league[keys.entity_twitter_id])
        for ht in re.findall(r"#(\w+)", ls[ProfileTwitter.description]):
            add_hash = '#' + ht
            if not ht.isdigit() and add_hash not in tweet:
                tweet.append(add_hash)
    except:
        pass
    return tweet

def get_blocked(site_name, social_key):
    from amazon import s3
    try:
        bucket = s3.bucket_straight(site_name)
        blocks_content = bucket.lookup('site/' + social_key + '_blocked.json').get_contents_as_string()
        return json.loads(blocks_content)
    except Exception as e:
        print 'blocks_content exception:', e
    return []
    
class MissingException(Exception):    
    pass
class MissingBackground(Exception):    
    pass
class MismatchException(Exception):
    pass        
class LeagueException(Exception):    
    pass

def validate_twitter(entity, check_exists = True):
    import requests
    from app import parse
    #print 'validate twitter:', entity[keys.entity_twitter]
    check_url = 'https://twitter.com/' + entity[keys.entity_twitter]
    check = requests.get(check_url, headers={'User-Agent': 'curl/7.35.0', 'Accept': '*/*'}, allow_redirects=False)        
    if check.status_code == 200:
        html = parse.html(check.text)
        #parse.dumpit(html, 'test.html')
        try:
            actual = html.cssselect('link[rel="alternate"][type="application/json+oembed"]')[0].attrib['href'].split('/')[-1]
        except:
            actual = html.cssselect('link[rel="alternate"][href^="android-app://"]')[0].attrib['href'].split('screen_name=')[1].split('&')[0]
            
        try:
            actual_id = html.cssselect('div[class="ProfileNav"][role="navigation"][data-user-id]')[0].attrib['data-user-id']
            actual_id = str(actual_id)
        except Exception as e:
            print e
            actual_id = None
        #print 'actual twitter:', actual, 'twitter_id:', actual_id, 'found twitter:', entity[keys.entity_twitter]
        if entity[keys.entity_twitter] != actual:
            #print 'change twitter:', entity[keys.entity_twitter], 'actual:', actual 
            entity[keys.entity_twitter] = actual
        if actual_id:
            entity[keys.entity_twitter_id] = actual_id
        
        if check_exists:
            return not keys.already_exists(entity[keys.entity_league], keys.entity_twitter, entity[keys.entity_twitter])
        else:
            return True
    
    if check.status_code == 302:
        print 'status code:', check.status_code, entity[keys.entity_twitter]
        print check.headers['location']
        return False 
    else:
        print 'status code:', check.status_code, entity[keys.entity_twitter]
        return False
