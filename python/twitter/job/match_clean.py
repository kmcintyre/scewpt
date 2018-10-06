import sys

from amazon.dynamo import Entity, User
from app import keys, user_keys, time_keys

def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

if sys.argv[1] == 'True':
    for e in Entity().scan(match_twitter__null=False):
        print e[keys.entity_profile]
        del e[keys.entity_match_twitter]
        e.partial_save()
else:
    user_leagues = User().get_leagues()
    user_league = [l for l in user_leagues if l[user_keys.user_role] == sys.argv[1]][0]        
    if len(sys.argv) > 2 and is_int(sys.argv[2]): 
        new_min_qualify = int(sys.argv[2])
        print 'set min qualify:', new_min_qualify                        
        user_league[user_keys.user_twitter_qualify] = int(new_min_qualify)
        user_league.partial_save()
    else:
        for e in Entity().query_2(league__eq=user_league[user_keys.user_role],query_filter={'match_twitter__null': False}):
            print e[keys.entity_profile]
            del e[keys.entity_match_twitter]
            e.partial_save()
        if len(sys.argv) > 2 and user_league[time_keys.ts_match_twitter]:
            del user_league[time_keys.ts_match_twitter]
            user_league.partial_save()