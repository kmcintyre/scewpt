from boto.dynamodb2.fields import HashKey, RangeKey, GlobalAllIndex, AllIndex
from boto.dynamodb2.table import Table, Item
from boto.dynamodb2.types import NUMBER

import time

from app import keys, fixed, time_keys, communication_keys, user_keys

from twitter import twitter_keys

allow_overwrite = True
standard_throughput={'read': 1,'write': 1}

class GenericTable(Table):

    def __init__(self, *args, **kwargs):
        super(GenericTable, self).__init__(self.table_name)
        self.use_boolean()

class Connection(GenericTable):
    
    table_name = 'connection'
        
    webrole = 'webrole'
    
    index_start = 'index_start'
    index_end = 'index_end'
    index_ip_key = 'index_ip_key' 

    def create(self):
        Table.create(
            self.table_name,
            schema=[
                 HashKey(communication_keys.websocket_key),
                 RangeKey(communication_keys.websocket_ip)
            ],
            throughput=standard_throughput,
            indexes={
               AllIndex(
                    self.index_start,
                    parts=[HashKey(communication_keys.websocket_key), RangeKey(communication_keys.websocket_ts_start, data_type=NUMBER)]
                ),                              
                AllIndex(
                    self.index_end,
                    parts=[HashKey(communication_keys.websocket_key), RangeKey(communication_keys.websocket_ts_end, data_type=NUMBER)]
                )
            },            
            global_indexes={
            }
        )
        print 'creating connection table'

    def new_client(self, data):
        item = Item(self, data=data)
        return item
  
class Entity(GenericTable):

    table_name = 'entity'
    
    index_wikipedia = 'index_wikipedia'
    index_twitter = 'index_twitter'
    index_instagram = 'index_instagram'
    index_facebook = 'index_facebook'
        
    index_twitter_league = 'index_twitter_league'
    index_facebook_league = 'index_facebook_league'
    index_instagram_league = 'index_instagram_league' 
    index_team_profile = 'index_team_profile'
    index_site_profile = 'index_site_profile'

    def create(self):
        Table.create(
            self.table_name,
            schema=[
                HashKey(keys.entity_league),
                RangeKey(keys.entity_profile)                                                  
            ],
            throughput=standard_throughput,
            indexes={
               AllIndex(
                    self.index_wikipedia,
                    parts=[HashKey(keys.entity_league), RangeKey(keys.entity_wikipedia)]
                ),                              
                AllIndex(
                    self.index_twitter,
                    parts=[HashKey(keys.entity_league), RangeKey(keys.entity_twitter)]
                ),
                AllIndex(
                    self.index_instagram,
                    parts=[HashKey(keys.entity_league), RangeKey(keys.entity_instagram)]
                ),
                AllIndex(
                    self.index_facebook,
                    parts=[ HashKey(keys.entity_league), RangeKey(keys.entity_facebook)]
                )
            },
            global_indexes={
                GlobalAllIndex(
                    self.index_twitter_league,
                    parts=[HashKey(keys.entity_twitter), RangeKey(keys.entity_league)],
                    throughput=standard_throughput
                ),
                GlobalAllIndex(
                    self.index_facebook_league,
                    parts=[ HashKey(keys.entity_facebook), RangeKey(keys.entity_league)],
                    throughput=standard_throughput
                ),
                GlobalAllIndex(
                    self.index_instagram_league,
                    parts=[HashKey(keys.entity_instagram), RangeKey(keys.entity_league)],
                    throughput=standard_throughput
                ),
                GlobalAllIndex(
                    self.index_team_profile,
                    parts=[HashKey(keys.entity_team), RangeKey(keys.entity_profile)],
                    throughput=standard_throughput
                ),
                GlobalAllIndex(
                    self.index_site_profile,
                    parts=[HashKey(keys.entity_site), RangeKey(keys.entity_profile) ],
                    throughput=standard_throughput
                )                     
            }
        )
        print 'creating entity next table'
    
    def language(self, entity, expr):
        if keys.entity_language in entity and expr in entity[keys.entity_language]:
            return entity[keys.entity_language][expr]
        else:
            if expr.endswith('(s)'):
                return self.language(entity, expr[:-3]) + 's'
            return expr
        
    def league_profile(self, league_name):
        return 'league:' + league_name
    
    def team_profile(self, team_name):
        return 'team:' + team_name
    
    def team_name(self, team_profile):
        return team_profile[5:]    
    
    def get_league_twitter(self, league_name, twitter):
        try:
            for entity in self.query_2(index=self.index_twitter_league, twitter__eq=twitter, league__eq=league_name, limit=1):
                return entity
        except:
            print 'except twitter:', league_name

    def get_league(self, league_name):
        try:
            return self.get_item(league=league_name, profile=self.league_profile(league_name))
        except:
            print 'except league:', league_name

    def get_operators(self, site_name = None):
        return User().get_leagues(site_name)
    
    def get_leagues(self, site_name = None):
        if site_name:               
            return self.batch_get([{'league': ln, 'profile': Entity().league_profile(ln)} for ln in User().get_league_names(site_name)])
        else:
            return self.batch_get([{'league': ln, 'profile': Entity().league_profile(ln)} for ln in User().get_league_names()])
    
class EntityHistory(GenericTable):
    
    table_name = 'entity_history'
    
    index_delta = 'index_delta'
    index_cut = 'index_cut'   
    
    index_site = 'index_site' 
    index_league = 'index_league' 
    index_twitter = 'index_twitter'
    index_team = 'index_team'
    
    def create(self):
        Table.create(
            self.table_name,
            schema=[
                 HashKey(keys.entity_profile),
                 RangeKey(time_keys.ts_add, data_type=NUMBER)
            ],
            throughput=standard_throughput,
            indexes={
                AllIndex(self.index_delta,
                          parts=[
                              HashKey(keys.entity_profile),
                              RangeKey(time_keys.ts_delta, data_type=NUMBER)
                          ]
                          ),                              
                 AllIndex(self.index_cut,
                          parts=[
                              HashKey(keys.entity_profile),
                              RangeKey(time_keys.ts_cut, data_type=NUMBER)
                          ]
                          )
            },
            global_indexes={
                GlobalAllIndex(
                    self.index_team,
                    parts=[HashKey(keys.entity_team), RangeKey(time_keys.ts_add, data_type=NUMBER)],
                    throughput=standard_throughput
                ),                            
                GlobalAllIndex(
                    self.index_league,
                    parts=[HashKey(keys.entity_league), RangeKey(time_keys.ts_add, data_type=NUMBER)],
                    throughput=standard_throughput
                ),
                GlobalAllIndex(
                    self.index_twitter,
                    parts=[HashKey(keys.entity_twitter), RangeKey(time_keys.ts_add, data_type=NUMBER)],
                    throughput=standard_throughput
                ),
                GlobalAllIndex(
                    self.index_site,
                    parts=[HashKey(keys.entity_site), RangeKey(time_keys.ts_add, data_type=NUMBER)],
                    throughput=standard_throughput
                )                            
            }
        )
        print 'creating entity history table'


    def last_cut(self, profile, league):
        try:
            return [e for e in self.query_2(index=EntityHistory.index_cut,profile__eq=profile, query_filter={'league__eq': league}, reverse=True, limit=1)][0]
        except:
            pass

    def last(self, profile, league):
        for e in self.query_2(profile__eq=profile, query_filter={'league__eq': league}, reverse=True, limit=1):
            return e

    def cut(self, league, cut):
        print 'cut player:', cut[keys.entity_profile]
        player = Entity().get_item(league=league, profile=cut[keys.entity_profile])
        cut_player = player._data
        cut_player[time_keys.ts_add] = int(time.time())
        cut_player[time_keys.ts_cut] = cut_player[time_keys.ts_add] 
        self.put_item(cut_player)
        player.delete()

    def archive(self, twitter, league=None, expo=None):
        print 'archive mising:', twitter, 'league:', league
        for p in Entity().query_2(index=Entity.index_twitter_league, twitter__eq=twitter):
            if not league or p[keys.entity_league] == league:
                print 'found archive:', p[keys.entity_league], p[keys.entity_profile]
                self.delta(p, { keys.entity_twitter + '__remove': p[keys.entity_twitter]})
                del p[keys.entity_twitter]
                p.save()
                                        
        
    def delta(self, delta_player, differences):
        try:
            print 'delta profile:', delta_player[keys.entity_profile]
        except:
            pass
        nd = {}                
        nd.update(differences)
        nd.update(delta_player._data)
        nd[time_keys.ts_add] = int(time.time())
        nd[time_keys.ts_delta] = nd[time_keys.ts_add]        
        try:
            return self.put_item(data=nd) 
        except Exception as e:
            print 'delta player exception:', e, delta_player._data, differences            

class Smtp(GenericTable):
    
    table_name = 'smtp'

    def create(self):
        Table.create(
            self.table_name,
            schema=[
                HashKey('derived_to'),
                RangeKey('derived_from')
            ],
            throughput=standard_throughput
        )
        print 'creating dynamo smtp table'
        
        
    def emails(self, d_to, d_from):
        try:            
            e = self.get_item(derived_to=d_to, derived_from=d_from)
            messages = e['msg'].split(',')
            messages.reverse()
            return messages
        except:
            print 'no emails to:', d_to, 'from:', d_from
            return []

class SocialMissing(GenericTable):
    
    table_name = 'social_missing'

    def create(self):
        Table.create(
            self.table_name,
             schema=[
                 HashKey(twitter_keys.tweet_id)                 
             ],
             throughput=standard_throughput,
        )
    
    def missing(self, t):
        item = Item(self, data=t)
        item.save()        
        
class SocialBeta(GenericTable):
    
    table_name = 'social_beta'
    index_social_ts_received = 'index_social_ts_received'

class TwitterProfile(GenericTable):
    
    table_name = 'twitter_profile'
    
    def profile_last(self, screen_name, since = None, ts_add = None):
        if ts_add:
            return self.get_item(screen_name=screen_name, ts_add=ts_add)
        kwargs = {
            'screen_name__eq' : screen_name,
            'reverse' : True,
            'limit' : 1
        }
        if since:
            kwargs['ts_add__gt'] = since
        for history in self.query_2(**kwargs):            
            return history 

class ProfileTwitter(GenericTable):
    
    table_name = 'profile_twitter'
    
    screen_name = 'screen_name'    
    description = 'description'    
    url = 'url'    
    
    translator_type = 'translator_type'
    one_week = 60 * 60 * 24 * 7
    photos_videos = 'photos_videos'
    moments = 'moments'
    vineloops = 'vineloops' 
    vine = 'vine'
    
    who_to_follow = 'who_to_follow'
    who_to_follow_promo = 'who_to_follow_promo'
    profile_banner_url = 'profile_banner_url'
    profile_image_url = 'profile_image_url'
    profile_background_color = 'profile_background_color'
    protected = 'protected'
    following = 'following'
    
    count_avi = 'count_avi'
    count_bg = 'count_bg'
    
    keys_delete = ['time_zone', 'utc_offset', 'has_extended_profile', 'ct_card', 'entities', 'profile_use_background_image', 'profile_background_image_url_https', 'profile_image_url_https', 'id', 'twitter', 'default_profile', 'lang', 'geo_enabled']    
    transform_keys = [('name', 'profile_name'), ('id_str', 'twitter_id'), ('screen_name', 'twitter')]
    
    def create(self):
        Table.create(
            self.table_name,
            schema=[
                HashKey(keys.entity_twitter_id),
                RangeKey(time_keys.ts_add, data_type=NUMBER),
            ],
            throughput=standard_throughput
        )
    
    def profile_clean(self, stats):
        for key in stats.keys():
            if isinstance(stats[key], bool) and not stats[key]:
                del stats[key]
        for tk in [ptk for ptk in self.transform_keys if ptk[0] in stats]:
            stats[tk[1]] = stats[tk[0]]
            del stats[tk[0]]
        for dk in [pdk for pdk in self.keys_delete if pdk in stats]:
            del stats[dk]          
        if self.translator_type in stats and stats[self.translator_type] == 'none':
            del stats[self.translator_type]
        return stats        
    
    def profile_new(self, stats):
        clean_stats = self.profile_clean(stats)
        clean_stats[time_keys.ts_add] = int(time.time())
        item = Item(self, data=clean_stats)                        
        item.save()        
        return item
    
    def profile_recent_time(self):
        return int(time.time()) - self.one_week
    
    def profile_recent(self, screen_name):        
        return self.profile_last(screen_name, self.profile_recent_time())
    
    def profile_args_since(self, twitter_id, since = None):
        kwargs = {
            'twitter_id__eq' : twitter_id,
            'reverse' : True,
            'limit' : 1
        }
        if since:
            kwargs['ts_add__gt'] = since
        return kwargs
    def profile_last(self, twitter_id, since = None, ts_add = None):
        if ts_add:
            return self.get_item(twitter_id=twitter_id, ts_add=ts_add)        
        for history in self.query_2(**self.profile_args_since(twitter_id, since)):            
            return history
        
class Tweet(GenericTable):
    
    table_name = 'tweet' 
       
    tweet_id = '_tweet_id'
    tweet_user_id = '_twitter_id'
    ts_ms = '_ts_ms'
    
    instagrams = 'instagrams'
    
    known_instagrams = 'known_instagrams'
    self_instagrams = 'self_instagrams'
    unknown_instagrams = 'unknown_instagrams'
    
    is_monologue = 'is_monologue'    
    known_conversation = 'known_conversation'    
        
    known_quote = 'known_quote'
    unknown_quote = 'unknown_quote'    
    
    known_retweet = 'known_retweet'
    unknown_retweet = 'unknown_retweet'
    
    known_mentions = 'known_mentions'
    
    index_timestamp = 'index_timestamp'
    index_tweet = 'index_tweet'
    index_retweet = 'index_retweet'
    
    index_league = 'index_league'
    index_site = 'index_site'
    index_team = 'index_team'
    
    def create(self):
        Table.create(
            self.table_name,
            schema=[
                HashKey(Tweet.tweet_user_id),
                RangeKey(Tweet.tweet_id),
            ],
            throughput=standard_throughput,
            indexes={
                AllIndex(
                    self.index_timestamp,
                    parts=[HashKey(Tweet.tweet_user_id), RangeKey(Tweet.ts_ms)]
                )                                          
            },                     
            global_indexes={
                GlobalAllIndex(
                    self.index_site,
                    parts=[HashKey(keys.entity_site), RangeKey(Tweet.tweet_id)],
                    throughput=standard_throughput
                ),
                GlobalAllIndex(
                    self.index_league,
                    parts=[HashKey(keys.entity_league), RangeKey(Tweet.tweet_id)],
                    throughput=standard_throughput
                ),
                GlobalAllIndex(
                    self.index_team,
                    parts=[HashKey(keys.entity_team), RangeKey(Tweet.tweet_id)],
                    throughput=standard_throughput
                )
            }                   
        )

#Tweet().create()

class TweetBeta(GenericTable):
    
    table_name = 'tweet_beta'

class User(GenericTable):

    table_name = 'user'
    index_role = 'index_role'

    def create(self):
        Table.create(
            self.table_name,
            schema=[
                HashKey('username'),
                RangeKey('password')
            ],
            throughput=standard_throughput
        )
        print 'creating dynamo user table'

    def get_role_args(self, role, account_type):
        kwargs = {'limit': 1}
        kwargs['role__eq'] = role                
        kwargs['index'] = self.index_role
        kwargs['query_filter'] = { 'type__eq': account_type}
        return kwargs
    
    def get_by_role(self, role, account_type):
        try:            
            return [u for u in self.query_2(**self.get_role_args(role, account_type))][0]
        except:
            print 'no user for role:', role
        return None

    def get_curator(self, league_name):
        for user in self.scan(site_leagues__contains=league_name):
            return user

    def get_league_names(self, site_name=None):
        leagues = []
        for site in [s for s in self.get_sites() if (s[user_keys.user_role] == site_name if site_name else True)]:
            leagues.extend(site[user_keys.user_site_leagues])
        return leagues
    
    def get_curators(self):
        curators = []
        for u in self.scan(role__contains='.com', inactive__null=True):
            curators.append(u)
        return curators
    
    def get_leagues(self, site_name=None, account_type = 'twitter'):
        leagues = []
        ln = self.get_league_names(site_name)
        for u in self.scan(inactive__null=True):
            if u[user_keys.user_role] in ln:
                if not account_type or u[user_keys.user_type] == account_type:
                    leagues.append(u)
        return leagues

    def get_sites(self):
        sites = []
        for u in self.scan(role__contains='.com', inactive__null=True):
            sites.append(u)
        return sites

class UserAvailable(User):

    table_name = 'user_available'
    
    def get_sites(self):
        sites = []
        for u in User().scan(role__contains='.com', inactive__null=True):
            sites.append(u)
        return sites


class UserSuspended(User):

    table_name = 'user_suspended'
    
    def get_sites(self):
        sites = []
        for u in User().scan(role__contains='.com', inactive__null=True):
            sites.append(u)
        return sites    
    
    