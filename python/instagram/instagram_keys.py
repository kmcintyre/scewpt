instagram_caption = 'instagram_caption'
instagram_name = 'instagram_name'
instagram_avi = 'instagram_avi'
instagram_url = 'instagram_url'
instagram_verified = 'instagram_verified'
by_tweet_instagram = 'by_tweet_instagram'

import pprint

from app import keys
import requests

def validate_instagram(entity, check_exists = True):
    print 'validate instagram:', entity[keys.entity_instagram]
    check_url = 'https://www.instagram.com/' + entity[keys.entity_instagram] + '/?__a=1'
    check = requests.get(check_url, headers={'User-Agent': 'curl/7.35.0', 'Accept': '*/*'}, allow_redirects=False)                                    
    print 'instagram response:', check_url, check.status_code
    if check.status_code == 200: 
        instagram_json = check.json()['graphql'] 
        if instagram_json['user']['username'] == entity[keys.entity_instagram]:
            entity[keys.entity_instagram_id] = instagram_json['user']['id']
            if check_exists:
                return not keys.already_exists(entity[keys.entity_league], keys.entity_instagram, entity[keys.entity_instagram])
            else:
                return True
    elif check.status_code == 404:
        del entity[keys.entity_instagram]
         
    return False