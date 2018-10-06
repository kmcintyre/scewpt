from app import keys, user_keys, fixed

from amazon.dynamo import Entity, User

import sys
league = []

for site in User().get_sites():
    for l in site[user_keys.user_site_leagues]:
        if len(sys.argv) < 2 or (site[user_keys.user_role] == sys.argv[1] or l == sys.argv[1]):                     
            entity_leauge = Entity().get_item(league=l, profile='league:' + l)
            if entity_leauge:
                league.append(entity_leauge)
        
league = sorted(league, key=lambda e2: str(e2[keys.entity_site]) + ' ' + str(e2[keys.entity_league]))
site = None
for l in league:
    u = User().get_by_role(l[keys.entity_league], keys.entity_twitter)
    print 'Site:', l[keys.entity_site], '%20s' % 'League:', l[keys.entity_league], '%10s' % 'Drops:' , fixed.no_drops(u), '%12s' % 'Qualify:', u[user_keys.user_twitter_qualify]
    entity_count = Entity().query_count(league__eq=l[keys.entity_league])
    entity_twitter_count = Entity().query_count(league__eq=l[keys.entity_league],query_filter={'twitter__null': False})
    entity_instagram_count = Entity().query_count(league__eq=l[keys.entity_league],query_filter={'instagram__null': False})
    print '%50s' % str(entity_count) + ' Total Players', '%18s' % str(entity_twitter_count) + ' Tweeters', '%18s' % str(entity_instagram_count) + ' Instagrams'
    count = Entity().query_count(league__eq=l[keys.entity_league],profile__beginswith ='team:')
    if count > 0:
        print '%15s' % (str(count) + ' Teams')
        for team in Entity().query_2(league__eq=l[keys.entity_league],profile__beginswith ='team:'):
            player_count = Entity().query_count(index=Entity.index_team_profile,team__eq=team[keys.entity_profile][5:], query_filter={'league__eq': l[keys.entity_league]})
            if player_count > 0:
                player_twitter_count = Entity().query_count(index=Entity.index_team_profile,team__eq=team[keys.entity_profile][5:],query_filter={'twitter__null': False, 'league__eq': l[keys.entity_league]})
                player_instagram_count = Entity().query_count(index=Entity.index_team_profile,team__eq=team[keys.entity_profile][5:],query_filter={'instagram__null': False, 'league__eq': l[keys.entity_league]})
                print '%40s' % Entity().team_name(team[keys.entity_profile]), '%15s' % str(player_count) + ' Players', '%15s' % str(player_twitter_count) + ' Tweeters', '%15s' % str(player_instagram_count) + ' Instagrams'
            else:
                team.delete()
    
        
    #if Entity().query_count(index=Entity.index_team_profile
    #entity_leauge = Entity().query_2(index=Entity.index_team_profile) league=l, profile='league:' + l)