pic = 'pic'
rank = 'rank'
position = 'position'

from app import keys, fixed, user_keys
import json
from amazon import s3
from amazon.dynamo import User

social_keys = [keys.entity_twitter_id, keys.entity_twitter, keys.entity_facebook, keys.entity_wikipedia, keys.entity_instagram, keys.entity_linkedin, keys.entity_snapchat, keys.entity_match_twitter]

def teamName(entity):
    if keys.entity_team in entity:
        return entity[keys.entity_team]
    else:
        return entity[keys.entity_profile][5:]
    
def get_blocked(site_name, social_key):
    try:
        bucket = s3.bucket_straight(site_name)
        blocks_content = bucket.lookup('site/' + social_key + '_blocked.json').get_contents_as_string()
        return json.loads(blocks_content)
    except Exception as e:
        print 'blocks_content exception:', e
    return []

def add_blocked(site_name, social_key, block):
    blocks = set(get_blocked(site_name, social_key))
    blocks.add(block.lower())
    content = json.dumps(blocks,cls=fixed.SetEncoder)
    bucket = s3.bucket_straight(site_name)
    s3.save_s3(bucket, 'site/' + social_key + '_blocked.json', content, None, 'application/json', 'public-read')
    return list(blocks)

def get_profile_overrides(league_name):
    print 'get_profile_overrides:', league_name 
    try:
        return json.loads(s3.bucket_straight(User().get_curator(league_name)[user_keys.user_role]).lookup('/' + league_name + '/profile_overrides.json').get_contents_as_string())
    except Exception as e:
        print 'profile overrides exception:', e 
    return {}