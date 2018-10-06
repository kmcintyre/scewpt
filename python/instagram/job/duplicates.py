from amazon.dynamo import Entity
from app import keys

instagram = []
duplicates = []
for e in Entity().scan(instagram__null=False):
    if e[keys.entity_instagram]:
        if e[keys.entity_instagram] not in [t[keys.entity_instagram] for t in instagram]:
            instagram.append({keys.entity_instagram: e[keys.entity_instagram], keys.entity_league: e[keys.entity_league]})
        else:
            t = [t for t in instagram if t[keys.entity_instagram] == e[keys.entity_instagram]][0]
            d = {}
            d.update(t)
            d['duplicate_instagram'] = e[keys.entity_instagram]
            d['duplicate_league'] = e[keys.entity_league]
            d['duplicate_profile'] = e[keys.entity_profile]
            print '{:17s}'.format(e[keys.entity_instagram]), '{:22s}'.format(e[keys.entity_league]), '    ', '{:17s}'.format(t[keys.entity_instagram]), '{:22s}'.format(t[keys.entity_league])
#for dup in duplicates:
#    print dup
