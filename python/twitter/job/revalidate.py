from amazon.dynamo import Entity
from twitter import twitter_keys
from app import keys

id_check = []

for e in Entity().scan(twitter__null = False):
    entity = {}
    entity[keys.entity_twitter] = e[keys.entity_twitter]
    if twitter_keys.validate_twitter(entity, False):
        if entity[keys.entity_twitter_id] != e[keys.entity_twitter_id]:
            print '    missing:', e['league'], e['twitter'], e['profile']   
    else:
        print '    missing:', e['league'], e['twitter'], e['profile']

