from amazon.dynamo import Entity
from app import keys
from instagram import instagram_keys
import time

for e in Entity().scan(instagram__null=False, instagram_id__null=True):
    print e[keys.entity_league], e[keys.entity_instagram]
    instagram_keys.validate_instagram(e, False)
    if e.needs_save(): 
        e.partial_save()
    time.sleep(10)