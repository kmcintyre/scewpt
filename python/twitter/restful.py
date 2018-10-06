from urllib import quote_plus
import pprint

import requests

import time

from app import keys, time_keys, user_keys

from twitter import auth
from twitter.twitter_util import StalkUtil

from amazon.dynamo import Entity

def mark_read_only(user, app_user):
    print 'mark as read only:', user[user_keys.user_role], app_user[user_keys.user_twitter_apps].keys()[0]
    user[user_keys.user_twitter_auth][app_user[user_keys.user_twitter_apps].keys()[0]][user_keys.user_read_only] = True
    user.partial_save()

def get_following_by_id(twitter_id, oauth):    
    url = 'https://api.twitter.com/1.1/users/lookup.json?include_entities=false&user_id={0}'.format(twitter_id)
    user_request = requests.get(url, auth=oauth)
    users = user_request.json()
    for u in users:
        try:
            del u['status']
        except:
            pass
    return users

def get_following(follows_list, oauth):    
    url_fmt = 'https://api.twitter.com/1.1/users/lookup.json?include_entities=false&screen_name={0}'
    url = url_fmt.format(','.join(follows_list))
    user_request = requests.get(url, auth=oauth)
    users = user_request.json()
    for u in users:
        try:
            del u['status']
        except:
            pass
    return users

def get_tweets(oauth, tweets):
    tweet_url = "https://api.twitter.com/1.1/statuses/lookup.json?id={0}".format(','.join(tweets))
    response = requests.post(tweet_url, auth=oauth)
    print 'response status code:', response
    response_json = response.json()
    pprint.pprint(response_json)
    return response_json    

def post_media(image_location, oauth, user):
    data = { 'media': (image_location.rsplit('/',)[1], open(image_location, 'rb'), 'image/' + image_location.rsplit('.',)[1]) }
    upload_url = "https://upload.twitter.com/1.1/media/upload.json"
    response = requests.post(upload_url, files=data, auth=oauth) #, headers={'Content-type': 'application/octet-stream'}
    response_json = response.json()
    print 'post media status code:', response.status_code
    if str(response.status_code).startswith('2'):
        return response_json['media_id_string']
    elif response.status_code == 403 and 'errors' in response_json and response_json['errors'][0]['code'] == 326:
        print 'user locked:', user[user_keys.user_role]
        user[user_keys.user_locked] = True
        user.partial_save()
    else:
        pprint.pprint(response_json)

def post_tweet(user, app_user, tweet_txt, image_location = None):
    try:
        oauth = auth.get_oauth(user, app_user, app_user[user_keys.user_twitter_apps].keys()[0])
        tweet_url_fmt = "https://api.twitter.com/1.1/statuses/update.json?status={0}"
        if image_location:
            media_id = post_media(image_location, oauth, user)
            if not media_id:
                return             
            print 'media_id:', media_id
            tweet_url_fmt += '&media_ids=' + media_id
        print tweet_txt.__class__.__name__ 
        if isinstance(tweet_txt, unicode):
            tweet_txt = tweet_txt.encode('utf-8') 
        tweet_url = tweet_url_fmt.format(quote_plus(tweet_txt))
        response = requests.post(tweet_url, auth=oauth)
        response_json = response.json()
        print 'post tweet status code:', response.status_code
        if str(response.status_code).startswith('2'):
            return True
        else:
            if response.status_code == 401 and 'error' in response_json and response_json['error'] == 'Read-only application cannot POST.':
                mark_read_only(user, app_user)
            elif response.status_code == 403 and 'errors' in response_json and response_json['errors'][0]['code'] == 261:
                mark_read_only(user, app_user)
            elif response.status_code == 403 and 'errors' in response_json and response_json['errors'][0]['code'] == 326:
                print 'user locked:', user[user_keys.user_role]
                user[user_keys.user_locked] = True
                user.partial_save()
            else:
                pprint.pprint(response.json())            
    except Exception as e:
        print 'post tweet exception:', e
    return False
            

def update_background(user, app_user, image_location):
    try:
        print 'update background:', user[user_keys.user_role], 'app user:', app_user[user_keys.user_role], 'app key:', app_user[user_keys.user_twitter_apps].keys()[0]
        data = { 'banner': (image_location.rsplit('/',)[1], open(image_location, 'rb'), 'image/' + image_location.rsplit('.',)[1]) }
        update_bg_url = 'https://api.twitter.com/1.1/account/update_profile_banner.json'        
        oauth = auth.get_oauth(user, app_user, app_user[user_keys.user_twitter_apps].keys()[0])
        response = requests.post(update_bg_url, files=data, auth=oauth)
        print 'update background status code:', response.status_code, response.json()
    except Exception as e:
        print 'update background exception:', e
        
def update_avatar(user, app_user, image_location):
    try:
        data = { 'image': (image_location.rsplit('/',)[1], open(image_location, 'rb'), 'image/' + image_location.rsplit('.',)[1]) }
        update_bg_url = 'https://api.twitter.com/1.1/account/update_profile_image.json'
        oauth = auth.get_oauth(user, app_user, app_user[user_keys.user_twitter_apps].keys()[0])
        response = requests.post(update_bg_url, files=data, auth=oauth)
        print 'update avatar:', response.status_code
    except Exception as e:
        print 'update avatar exception:', e        
        
def get_lists(user, app_user, oauth = None):
    try:
        list_url = 'https://api.twitter.com/1.1/lists/list.json'
        if not oauth:
            oauth = auth.get_oauth(user, app_user, app_user[user_keys.user_twitter_apps].keys()[0])
        response = requests.get(list_url, auth=oauth)
        response_json = response.json()        
        if str(response.status_code).startswith('2'):
            return response_json
        else:
            pprint.pprint(response_json)
            exit()
    except Exception as e:
        print 'get lists exception:', e

def create_list(user, app_user, list_name, description, oauth = None):
    try:
        data = {'name': list_name, 'description': description}
        create_list_url = 'https://api.twitter.com/1.1/lists/create.json'
        if not oauth:
            oauth = auth.get_oauth(user, app_user, app_user[user_keys.user_twitter_apps].keys()[0])
        response = requests.post(create_list_url, data=data, auth=oauth)
        response_json = response.json()
        print 'create lists status code:', response.status_code
        if str(response.status_code).startswith('2'):
            return response_json
        else:
            pprint.pprint(response_json)
            exit()        
    except Exception as e:
        print 'create list exception:', e        

def list_members(user, app_user, list_id, oauth):
    try:
        members = []
        if not oauth:
            oauth = auth.get_oauth(user, app_user, app_user[user_keys.user_twitter_apps].keys()[0])
        cursor = -1
        while cursor != 0: 
            members_list_url = 'https://api.twitter.com/1.1/lists/members.json?count=5000&list_id=' + str(list_id) + '&cursor=' + str(cursor)
            print 'members list url:', members_list_url
            response = requests.get(members_list_url, auth=oauth)
            print 'list members status code:', response.status_code
            response_json = response.json()
            if str(response.status_code).startswith('2'):                
                cursor = response_json['next_cursor']
                for u in response_json['users']:
                    members.append(u['screen_name'])
            else:
                pprint.pprint(response_json)
        return members
    except Exception as e:
        print 'list members exception:', e        
        
def list_add_members(user, app_user, list_id, members, oauth = None):
    try:        
        if not oauth:
            oauth = auth.get_oauth(user, app_user, app_user[user_keys.user_twitter_apps].keys()[0])
        members_list_url = 'https://api.twitter.com/1.1/lists/members/create_all.json?list_id=' + str(list_id) + '&screen_name=' + ','.join(members)
        response = requests.post(members_list_url, auth=oauth)
        response_json = response.json()
        print 'list add members status code:', response.status_code             
        if str(response.status_code).startswith('2'):
            return response_json
        else:
            pprint.pprint(response_json)
    except Exception as e:
        print 'add lists exception:', e

def list_remove_members(user, app_user, list_id, members, oauth = None):
    try:        
        if not oauth:
            oauth = auth.get_oauth(user, app_user, app_user[user_keys.user_twitter_apps].keys()[0])
        members_list_url = 'https://api.twitter.com/1.1/lists/members/destroy_all.json?list_id=' + str(list_id) + '&screen_name=' + ','.join(members)
        response = requests.post(members_list_url, auth=oauth)
        response_json = response.json()
        print 'list remove members status code:', response.status_code             
        if str(response.status_code).startswith('2'):
            return response_json
        elif response.status_code == 403:
            if 'errors' in response_json and response_json['errors'][0]['code'] == 108:
                for member in members:
                    check = requests.get('https://twitter.com/' + member, headers={'User-Agent': 'curl/7.35.0', 'Accept': '*/*'}, allow_redirects=False)        
                    if check.status_code != 200:
                        for entity in Entity().query_2(index=Entity.index_twitter_league, twitter__eq=member):
                            StalkUtil().recover(entity)
                    members.remove(member)
                list_remove_members(user, app_user, list_id, members, oauth)
            else:
                pprint.pprint(response_json)
        else:
            pprint.pprint(response_json)
            
    except Exception as e:
        print 'add lists exception:', e

class Inflate(object):

    def get_screen_names(self, user_ids, oauth):
        lookup_fmt = 'https://api.twitter.com/1.1/users/lookup.json?user_id={0}&include_entities=false'
        lookup_url = lookup_fmt.format(','.join(user_ids))
        print 'url:', lookup_url
        return [u['screen_name'] for u in requests.get(lookup_url, auth=oauth).json()]
    
    def do_inflate(self, user, app_user):
        oauth = auth.get_oauth(user, app_user, app_user[user_keys.user_twitter_apps].keys()[0])        
        print 'oauth:', oauth    
        following = []
        cursor = -1
        count = 0
        while cursor != 0:        
            ids_fmt = 'https://api.twitter.com/1.1/friends/ids.json?cursor={0}&screen_name={1}&count=5000'
            ids_url = ids_fmt.format(cursor, user[keys.entity_twitter])
            print 'url:', ids_url
            ids_request = requests.get(ids_url, auth=oauth)
            ids_response = ids_request.json()
            if 'errors' in ids_response:
                if ids_response['errors'][0]['code'] == 326:
                    pprint.pprint(ids_response)
                    user[user_keys.user_locked] = True
                    user[time_keys.ts_inflated] = int(time.time())
                    user.partial_save()                    
                    exit()                                            
                else: 
                    pprint.pprint(ids_response)
                    exit()
            cursor = ids_response['next_cursor']
            ids = ids_response['ids']
            user_ids = []
            while len(ids) > 0:
                user_id = ids.pop()
                user_ids.append(str(user_id))
                if len(user_ids) == 100:
                    following.extend(self.get_screen_names(user_ids, oauth))
                    user_ids = [] 
            if len(user_ids) > 0:
                following.extend(self.get_screen_names(user_ids, oauth))            
        print 'following:', following
        for e in Entity().query_2(index=Entity.index_twitter, league__eq=user[user_keys.user_role]):
            if e[keys.entity_twitter] not in following:
                print e[keys.entity_twitter]
                follow_fmt = 'https://api.twitter.com/1.1/friendships/create.json?screen_name={0}&follow=false'
                follow_url = follow_fmt.format(e[keys.entity_twitter])
                follow_request = requests.post(follow_url, auth=oauth)
                
                follow_response = follow_request.json()
                if 'screen_name' in follow_response:
                    count += 1
                    print 'followed:', follow_response['screen_name'], count, e[keys.entity_profile]
                    if count > 100:
                        user[time_keys.ts_inflated] = int(time.time())
                        user.partial_save()
                        exit()
                elif 'errors' in follow_response:                                    
                    if follow_response['errors'][0]['code'] == 108:
                        print 'lost user:', e[keys.entity_twitter]
                        StalkUtil().recover(e)
                    elif follow_response['errors'][0]['code'] == 162:                        
                        print 'blocked:', e[keys.entity_twitter]                                
                    elif follow_response['errors'][0]['code'] == 160:                        
                        print 'already requested:', e[keys.entity_twitter]
                    elif follow_response['errors'][0]['code'] == 326:
                        pprint.pprint(follow_response)
                        user[user_keys.user_locked] = True
                        user[time_keys.ts_inflated] = int(time.time())
                        user.partial_save()                    
                        exit()                                            
                    else: 
                        pprint.pprint(follow_response)
                        user[time_keys.ts_inflated] = int(time.time())
                        user.partial_save()                    
                        exit()
                elif follow_request.status_code == 401 and 'error' in follow_response and follow_response['error'] == 'Read-only application cannot POST.':
                    print 'mark as read only:', user[user_keys.user_role], app_user[user_keys.user_twitter_apps].keys()[0]
                    user[user_keys.user_twitter_auth][app_user[user_keys.user_twitter_apps].keys()[0]][user_keys.user_read_only] = True
                    user[time_keys.ts_inflated] = int(time.time())
                    user.partial_save()
                    exit()                   
                else:
                    pprint.pprint(follow_response)
                    user[time_keys.ts_inflated] = int(time.time())
                    user.partial_save()                                    
                    exit()            
                time.sleep(5)
            else:
                print 'already follows:', e[keys.entity_twitter]
                following.remove(e[keys.entity_twitter])
        user[time_keys.ts_inflated] = int(time.time())
        print 'extra:', following
        for d in following:
            drop_fmt = 'https://api.twitter.com/1.1/friendships/destroy.json?screen_name={0}'
            drop_url = drop_fmt.format(d)
            drop_request = requests.post(drop_url, auth=oauth)
            print 'drop:', d, 'status code:', drop_request.status_code
            time.sleep(2)
        user.partial_save()
