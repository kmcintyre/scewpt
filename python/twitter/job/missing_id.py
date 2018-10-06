from amazon.dynamo import Entity
from app import keys
from twitter import twitter_keys

for e in Entity().scan(twitter__null=False, twitter_id__null=True):
    print e[keys.entity_league], e[keys.entity_twitter]
    if not twitter_keys.validate_twitter(e, False):
        print e[keys.entity_league], e[keys.entity_profile], e.keys()
        del e[keys.entity_twitter]   
        del e[keys.entity_twitter_id]
        del e[keys.entity_match_twitter]
        for k in [dk for dk in e._data.keys() if dk.startswith('ts_')]:
            del e[k]
    if e.needs_save(): 
        e.partial_save()