from amazon.dynamo import Entity, User
from app import fixed, keys, user_keys
from league import keys_league
import os.path
import sys

leagues = []
if len(sys.argv) > 1:
    leagues.append(sys.argv[1])

for u in User().scan(site_leagues__null=False):
    for league in [l for l in u[user_keys.user_site_leagues] if not leagues or l in leagues]:
        print u[user_keys.user_role], league
        for e in Entity().query_2(league__eq=league, profile__beginswith='team:'):
            
            logo = '/home/ubuntu/' + u[user_keys.user_role] + '/' + league + '/logo/' + fixed.simplify_to_id(keys_league.teamName(e)) + '.svg'
            if not os.path.isfile(logo):
                print 'missing svg:', logo
            #logo2 = '/home/ubuntu/' + u[user_keys.user_role] + '/' + league + '/logo/' + fixed.simplify_to_id(keys_league.teamName(e)) + '.png'
            #if not os.path.isfile(logo):
            #    print 'missing png:', logo2
