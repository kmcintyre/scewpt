from app import keys, fixed, user_keys, time_keys

from amazon.dynamo import Entity, User

from twisted.internet import reactor, defer, task 

import sys
import time
sites = []
leagues = []
import requests

def print_operator_curator(entity):
    print entity[user_keys.user_role] if entity[user_keys.user_role] else entity[keys.entity_profile] , 'entity:', entity[keys.count('entity')], 'team:', entity[keys.count(keys.entity_team)], 'league:', entity[keys.count(keys.entity_league)], 'twitter:', entity[keys.count(keys.entity_twitter)], 'instagram:', entity[keys.count(keys.entity_instagram)], 'facebook:', entity[keys.count(keys.entity_facebook)]


@defer.inlineCallbacks
def run_counts():
    for site in User().get_sites():
        print 'site yield'
        yield task.deferLater(reactor, 10, defer.succeed, True)    
        if True or not site[time_keys.ts_count]:
            print 'site counts since:', fixed.lingo_since_date(site[time_keys.ts_count])            
            _ec = Entity().query_count(index=Entity.index_site_profile, site__eq=site[user_keys.user_role])
            _tc = Entity().query_count(index=Entity.index_site_profile, site__eq=site[user_keys.user_role], profile__beginswith='team:')
            _lc = Entity().query_count(index=Entity.index_site_profile, site__eq=site[user_keys.user_role], profile__beginswith='league:')
            _twc = Entity().query_count(index=Entity.index_site_profile, site__eq=site[user_keys.user_role], query_filter={'twitter__null': False})
            _iwc = Entity().query_count(index=Entity.index_site_profile, site__eq=site[user_keys.user_role], query_filter={'instagram__null': False})
            _fwc = Entity().query_count(index=Entity.index_site_profile, site__eq=site[user_keys.user_role], query_filter={'facebook__null': False})
            site[keys.count('entity')] = _ec
            site[keys.count(keys.entity_team)] = _tc
            site[keys.count(keys.entity_league)] = _lc
            site[keys.count(keys.entity_twitter)] = _twc
            site[keys.count(keys.entity_instagram)] = _iwc
            site[keys.count(keys.entity_facebook)] = _fwc
            site[time_keys.ts_count] = int(time.time())
            site.partial_save()
        else:
            print 'site counts since:', fixed.lingo_since_date(site[time_keys.ts_count])
        print_operator_curator(site)
        for l in site[user_keys.user_site_leagues]:
            print 'league yield'
            yield task.deferLater(reactor, 10, defer.succeed, True)        
            curator = User().get_by_role(l, keys.entity_twitter)
            if True or not curator[time_keys.ts_count]:
                print 'league counts since:', fixed.lingo_since_date(curator[time_keys.ts_count])                
                tc = Entity().query_count(league__eq=curator[user_keys.user_role], profile__beginswith='team:')
                ec = Entity().query_count(league__eq=curator[user_keys.user_role])
                twc = Entity().query_count(league__eq=curator[user_keys.user_role], query_filter={'twitter__null': False})
                iwc = Entity().query_count(league__eq=curator[user_keys.user_role], query_filter={'instagram__null': False})
                fwc = Entity().query_count(league__eq=curator[user_keys.user_role], query_filter={'facebook__null': False})
                curator[keys.count('entity')] = ec
                curator[keys.count(keys.entity_team)] = tc
                curator[keys.count(keys.entity_twitter)] = twc
                curator[keys.count(keys.entity_instagram)] = iwc
                curator[keys.count(keys.entity_facebook)] = fwc
                curator[time_keys.ts_count] = int(time.time())
                curator.partial_save()
                #for team in Entity().query_2(league__eq=curator[user_keys.user_role], profile__beginswith='team:'):
                #    print 'team yield'
                #    yield task.deferLater(reactor, 10, defer.succeed, True)                    
                #    team_url = 'http://service.' + site[user_keys.user_role] + '/site/' + curator[user_keys.user_role] + '/' + team[keys.entity_profile].split(':', 1)[1] + '/players'
                #    print 'team:', team_url
                #    r = requests.get(team_url)
                #    print r.status_code
                #teams_url = 'http://service.' + site[user_keys.user_role] + '/site/' + curator[user_keys.user_role] + '/teams'
                #print 'teams:', teams_url
                #requests.get(teams_url)                                        
            else:
                print '    league counts since:', fixed.lingo_since_date(curator[time_keys.ts_count])
            print_operator_curator(curator)
        site_url = 'http://service.' + site[user_keys.user_role] + '/site/curator'
        print 'site:', site_url
        requests.get(site_url)
        operators_url = 'http://service.' + site[user_keys.user_role] + '/site/operators'
        print 'operators:', operators_url
        requests.get(operators_url)
    yield task.deferLater(reactor, 10, defer.succeed, True)
    reactor.callLater(0, reactor.stop)
if __name__ == '__main__':
    reactor.callWhenRunning(run_counts)
    reactor.run()
    
    

'''
sorted_leagues = sorted(leagues, key=lambda e2: str(e2[keys.entity_site]) + ' ' + str(e2[keys.entity_league]))
for l in sorted_leagues:

def get_site(site):
    return [s for s in sites if site[user_keys.user_role] == site]
for l in sorted_leagues:
    
    site.
            
for l in league:
    u = User().get_by_role(l[keys.entity_league], keys.entity_twitter)
    print 'Site:', l[keys.entity_site], '%20s' % 'League:', l[keys.entity_league], '%10s' % 'Drops:' , twutil.no_drops(u), '%12s' % 'Qualify:', u[keys.user_twitter_qualify]
    entity_count = Entity().query_count(league__eq=l[keys.entity_league])
    entity_twitter_count = Entity().query_count(league__eq=l[keys.entity_league],query_filter={'twitter__null': False})
    entity_instagram_count = Entity().query_count(league__eq=l[keys.entity_league],query_filter={'instagram__null': False})
    print '%50s' % str(entity_count) + ' Total Players', '%18s' % str(entity_twitter_count) + ' Tweeters', '%18s' % str(entity_instagram_count) + ' Instagrams'
    count = Entity().query_count(league__eq=l[keys.entity_league],profile__beginswith ='team:')
    if count > 0:
        print '%15s' % (str(count) + ' Teams')
        for team in Entity().query_2(league__eq=l[keys.entity_league],profile__beginswith ='team:'):
            player_count = Entity().query_count(index=Entity.index_team_profile,team__eq=team[keys.entity_profile][5:])
            if player_count > -1:
                player_twitter_count = Entity().query_count(index=Entity.index_team_profile,team__eq=team[keys.entity_profile][5:],query_filter={'twitter__null': False})
                player_instagram_count = Entity().query_count(index=Entity.index_team_profile,team__eq=team[keys.entity_profile][5:],query_filter={'instagram__null': False})
                print '%40s' % Entity().team_name(team[keys.entity_profile]), '%15s' % str(player_count) + ' Players', '%15s' % str(player_twitter_count) + ' Tweeters', '%15s' % str(player_instagram_count) + ' Instagrams'
            else:
                team.delete()
'''    
        
    #if Entity().query_count(index=Entity.index_team_profile
    #entity_leauge = Entity().query_2(index=Entity.index_team_profile) league=l, profile='league:' + l)
        
