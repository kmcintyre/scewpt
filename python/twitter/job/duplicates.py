from amazon.dynamo import Entity
from app import keys

twitter = []
duplicates = []
for e in Entity().scan(twitter__null=False):
    if e[keys.entity_twitter]:
        if e[keys.entity_twitter] not in [t[keys.entity_twitter] for t in twitter]:
            twitter.append({keys.entity_twitter: e[keys.entity_twitter], keys.entity_league: e[keys.entity_league]})
        else:
            t = [t for t in twitter if t[keys.entity_twitter] == e[keys.entity_twitter]][0]
            d = {}
            d.update(t)
            d['duplicate_twitter'] = e[keys.entity_twitter]
            d['duplicate_league'] = e[keys.entity_league]
            d['duplicate_profile'] = e[keys.entity_profile]
            print '{:17s}'.format(e[keys.entity_twitter]), '{:22s}'.format(e[keys.entity_league]), '    ', '{:17s}'.format(t[keys.entity_twitter]), '{:22s}'.format(t[keys.entity_league])
#for dup in duplicates:
#    print dup
