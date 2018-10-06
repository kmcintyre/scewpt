from amazon.dynamo import User, Entity, ProfileTwitter
from twitter import twitter_util, auth, twitter_keys, restful
from app import keys, fixed, time_keys, user_keys, misc

from twitter.job import lists
from amazon.sqs import AvatarQueue, BackgroundQueue

import time
import sys
import urllib2
import os
import subprocess
import requests
from urlparse import urlparse
from PIL import Image
from twitter import tweets

from amazon import s3  
from boto.dynamodb2.exceptions import ConditionalCheckFailedException

do_tweet = True

def delete_sets_and_lists(obj):
    compare_data = {}
    compare_data.update(obj)
    for sk in [k for k in compare_data.keys() if isinstance(compare_data[k], set) or isinstance(compare_data[k], list)]:
        del compare_data[sk]
    return compare_data
        
def comparable(obj):
    compare_data = {}
    compare_data.update(obj._data)    
    return delete_sets_and_lists(compare_data)

def small_sync(entity, current):
    avi_sm_url = '_bigger'.join(current[ProfileTwitter.profile_image_url].rsplit('_normal', 1))    
    local_small_avi_path = '/tmp/sm_' + entity[keys.entity_twitter] + avi_sm_url[avi_sm_url.rindex('.'):]
    try:        
        with open(local_small_avi_path, 'w') as small_file:
            response = urllib2.urlopen(avi_sm_url).read()
            small_file.write(response)                             
        resize_args = ['convert', local_small_avi_path, '-resize', '48x48^', local_small_avi_path]            
        subprocess.check_call(resize_args)        
        if local_small_avi_path[-3:].lower() == 'jpg' or local_small_avi_path[-4:].lower() == 'jpeg':                
            new_local_small_avi_path = '/tmp/sm_' + entity[keys.entity_twitter] + '.png'                
            args = ['convert', local_small_avi_path, new_local_small_avi_path]
            subprocess.check_call(args)
            local_small_avi_path = new_local_small_avi_path                                                    
        misc.round_corners(local_small_avi_path, 'small')                        
        sm_meta = {}
        sm_meta.update(current)
        sm_meta.update(entity._data)    
        avi_small_for_hash = '_400x400'.join(current[ProfileTwitter.profile_image_url].rsplit('_normal', 1))
        s3.save_avi('small', avi_small_for_hash, local_small_avi_path, sm_meta)
    except Exception as e:
        print 'small sync exception:', e  

def comparing(curator, user, twitter, current, old, profile):
    current_set = set(delete_sets_and_lists(ProfileTwitter().profile_clean(current)).items())
    old_set = set(old.items())
    c1 = dict(current_set - old_set)    
    '''
    c2 = dict(old_set - current_set)
    print 'new keys:'
    print c1.keys()
    print 'old keys:' 
    print c2.keys()
    '''
    if ProfileTwitter.profile_banner_url in c1:
        print 'background update:', twitter, current[ProfileTwitter.profile_banner_url]
        bg_compare_url = current[ProfileTwitter.profile_banner_url] + '/1500x500'
        bg_url = fixed.clean_url(bg_compare_url)
        try:
            response = urllib2.urlopen(bg_url)
            background_img = response.read()
            local_path = '/tmp/' + twitter + '/bgimage'
            try:
                os.makedirs(os.path.dirname(local_path))
            except:
                pass
            bgimage_file = open(local_path, 'w')
            bgimage_file.write(background_img)
            bgimage_file.close()
            im = Image.open(local_path)
            new_local_path = local_path + '.png'
            im.save(new_local_path)
            entity = Entity().get_league_twitter(user[user_keys.user_role], twitter)
            
            entity_meta = {}
            entity_meta.update(current)
            entity_meta.update(entity._data)
            
            s3.save_bg(bg_compare_url, new_local_path, entity_meta)
            bg_count = len(s3.get_twitter_media(entity, 'background'))
            profile[ProfileTwitter.count_bg] = bg_count
            profile.partial_save()            
            try:
                profile[ProfileTwitter.profile_banner_url] = current[ProfileTwitter.profile_banner_url]
            except:
                pass
            if do_tweet:                      
                
                bg_tweet = tweets.bg_tweet(curator, Entity().get_league(user[user_keys.user_role]), entity, bg_count)
                try:                    
                    print 'background tweet:', bg_tweet
                except:
                    pass                                
                tweet_message = {}
                tweet_message.update(entity._data)                            
                tweet_message[twitter_keys.message_tweet] = bg_tweet
                BackgroundQueue().createMessage(tweet_message)
        except Exception as e:
            print 'missing background image:', e
    
    if ProfileTwitter.profile_image_url in c1:
        print 'avatar update:', twitter, current[ProfileTwitter.profile_image_url]
        avi_compare_url = '_400x400'.join(current[ProfileTwitter.profile_image_url].rsplit('_normal', 1))
        avi_url = fixed.clean_url(avi_compare_url)
        local_large_avi_path = '/tmp/large/' + twitter + avi_url[avi_url.rindex('.'):]
        fixed.filesubpath(local_large_avi_path)
        resize_local_large_avi_path = '/tmp/resize/large/' + twitter + '.png'
        fixed.filesubpath(resize_local_large_avi_path)            
        try:
            with open(local_large_avi_path, 'w') as large_file:
                response = urllib2.urlopen(avi_compare_url).read()
                large_file.write(response)
                #print 'done writing to file', local_large_avi_path
            if local_large_avi_path[-3:].lower() == 'jpg' or local_large_avi_path[-4:].lower() == 'jpeg':
                new_local_large_avi_path = '/tmp/large/png/' + twitter + '.png'
                fixed.filesubpath(new_local_large_avi_path)
                args = ['convert', local_large_avi_path, new_local_large_avi_path]
                subprocess.check_call(args)
                local_large_avi_path = new_local_large_avi_path                                    
            
            entity = Entity().get_league_twitter(user[user_keys.user_role], twitter)
            avi_meta = {}
            avi_meta.update(current)
            avi_meta.update(entity._data)
            
            s3.save_avi('orig', avi_compare_url, local_large_avi_path, avi_meta)            
            resize_args = ['convert', local_large_avi_path, '-resize', '210x210^', resize_local_large_avi_path]
            subprocess.check_call(resize_args)                
            misc.round_corners(resize_local_large_avi_path, 'large')                            
            s3.save_avi('large', avi_compare_url, resize_local_large_avi_path, avi_meta)
            avi_count = len(s3.get_twitter_media(entity, 'large'))
            profile[ProfileTwitter.count_avi] = avi_count
            profile.partial_save()     
            try:
                profile[ProfileTwitter.profile_image_url] = current[ProfileTwitter.profile_image_url]
            except:
                pass       
            if do_tweet:
                
                avi_tweet = tweets.avi_tweet(curator, Entity().get_league(user[user_keys.user_role]), entity, avi_count)
                try:
                    print 'avi tweet:', avi_tweet
                except:
                    pass
                tweet_message = {}
                tweet_message.update(entity._data)
                tweet_message[twitter_keys.message_tweet] = avi_tweet
                AvatarQueue().createMessage(tweet_message)                
            small_sync(entity, current)                                
        except:
            print 'missing avatar image!'

def verify_media(p, league_name, force = False):
    if ProfileTwitter.url in p and urlparse(p[ProfileTwitter.url]).netloc == 't.co':
        r = requests.get(p[ProfileTwitter.url], allow_redirects=False)
        if r.status_code == 301:
            print 'fix location:', p[ProfileTwitter.url], r.headers['Location'], p[ProfileTwitter]
            p[ProfileTwitter.url] = r.headers['Location'] 
    if not p[ProfileTwitter.count_avi] or force:
        tw_avi_count = len(s3.get_twitter_media({ keys.entity_twitter_id: str(p['id']) }, 'large'))
        p[ProfileTwitter.count_avi] = tw_avi_count 
    if not p[ProfileTwitter.count_bg] or force:
        tw_bg_count = len(s3.get_twitter_media({ keys.entity_twitter_id: str(p['id']) }, 'background'))
        p[ProfileTwitter.count_bg] = tw_bg_count
    for dk in [k for k in p._data.keys() if (k.endswith('_mutual') or k.endswith('_follows')) and not k.startswith(league_name)]:
        print 'delete:', league_name, 'key:', dk
        del p[dk]
    if p.needs_save():
        print p[keys.entity_twitter_id], 'avi count:', p[ProfileTwitter.count_avi], 'background count:', p[ProfileTwitter.count_bg], p[ProfileTwitter.url] if ProfileTwitter.url in p else 'No Url'
        p.partial_save()
   
def do_compare(curator, user, f, entity):
    recent = ProfileTwitter().profile_recent(f['id_str'])
    if not recent:
        last = ProfileTwitter().profile_last(f['id_str'])
        profile_data = {}
        if last:
            profile_data.update(last._data)
        profile_data.update(f)     
        profile = ProfileTwitter().profile_new(profile_data)
        print 'creating profile:', profile[keys.entity_twitter]
        verify_media(profile, user[user_keys.user_role])
        if last:            
            comparing(curator, user, f[ProfileTwitter.screen_name], comparable(profile), comparable(last), profile)
        else:
            comparing(curator, user, f[ProfileTwitter.screen_name], comparable(profile), {}, profile)
        entity[time_keys.ts_scout] = profile[time_keys.ts_add]
        entity.partial_save()        
    else:
        verify_media(recent, user[user_keys.user_role])        
        print 'skipping sync:', f[ProfileTwitter.screen_name]
        comparing(curator, user, f[ProfileTwitter.screen_name], delete_sets_and_lists(f), comparable(recent), recent)
        if not entity[time_keys.ts_scout] or entity[time_keys.ts_scout] != recent[time_keys.ts_add]:
            print 'update time:', entity[time_keys.ts_scout], recent[time_keys.ts_add], recent[time_keys.ts_add].__class__.__name__
            entity[time_keys.ts_scout] = recent[time_keys.ts_add]
            entity.partial_save()
        if recent.needs_save():
            recent.partial_save() 
        

def follows_subset(curator, user, follows_list, oauth):
    users = restful.get_following([f[keys.entity_twitter] for f in follows_list], oauth)
    for u in users:
        try:
            l = [l for l in follows_list if l[keys.entity_twitter] == u[ProfileTwitter.screen_name]][0]
            follows_list.remove(l)
            do_compare(curator, user, u, l)
        except ConditionalCheckFailedException as e:
            print 'conditional failed:', u[ProfileTwitter.screen_name], len(follows_list)
        except Exception as e:
            print 'exception do compare:', e, u[ProfileTwitter.screen_name], len(follows_list)
    for lost in follows_list:
        twitter_util.StalkUtil().recover(lost)

def scout_report(sr):    
    for index, league in enumerate(sr):
        print '{:3s}'.format(str(index+1)), '{:6s}'.format('True' if league[user_keys.user_locked] else 'False'), '{:20s}'.format(league[user_keys.user_role]), 'since scouted:', fixed.lingo_since(league, time_keys.ts_pin)

if __name__ == '__main__':
    leagues = User().get_leagues()
    leagues = sorted(leagues, key=lambda item: item[time_keys.ts_pin])
    def get_league(arg):
        if arg == 'True':
            return leagues[0]
        elif arg.isdigit():
            return leagues[int(arg)-1]
        return [l for l in leagues if l[user_keys.user_role] == arg][0]            
    if len(sys.argv) > 1:
        user = get_league(sys.argv[1])        
        universal = User().get_by_role('me', keys.entity_twitter)
        print 'scout:', user[user_keys.user_role] 
        curator = User().get_curator(user[user_keys.user_role])        
        oauth = auth.get_oauth(universal, universal, universal[user_keys.user_twitter_apps].keys()[0])
        follows = []            
        for e in Entity().query_2(index=Entity.index_twitter, league__eq=user[user_keys.user_role]):
            follows.append(e)
            if len(follows) == 100:
                follows_subset(curator, user, follows, oauth)
                follows = []    
        if len(follows) > 0:
            follows_subset(curator, user, follows, oauth)                

        print 'marking as scouted'
        user[time_keys.ts_pin] = int(time.time())        
        user.partial_save()
        
        if not user[user_keys.user_locked] and user[user_keys.user_twitter_auth]:            
            if curator[user_keys.user_role] in ['d1tweets.com','athleets.com']:
                if user[user_keys.user_role] not in ['tennis', 'golf']:
                    lists.league_lists(user[user_keys.user_role])
                lists.curator_lists(curator[user_keys.user_role], user[user_keys.user_role])
            elif user[user_keys.user_role] in ['startup']:
                lists.league_lists(user[user_keys.user_role])
                lists.curator_lists(curator[user_keys.user_role], user[user_keys.user_role])                                        
    else:
        scout_report(leagues)