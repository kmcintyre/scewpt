from twitter import tweets
from app import keys, time_keys, user_keys

from amazon import s3

from app import fixed
from twitter import restful, twitter_keys, auth

from amazon.dynamo import Entity, EntityHistory, User
from amazon.sqs import TweetQueue
from twisted.internet import defer, reactor

from twisted.web import client
client._HTTP11ClientFactory.noisy = False

import time
import json
import simplejson
import pprint

from app import parse

class Common(object):
    
    chrome_scraper = True
    chrome_fresh = True
    chrome_width = 1200
    chrome_height = 800
    
    rank_difference_filter = 0    
    prune_keys = []
        
    def prune_dups(self, entities):
        print 'prune dups:', len(entities)
        pruned = []
        for e in entities:
            try:
                if keys.entity_profile in e and e[keys.entity_profile] not in [p[keys.entity_profile] for p in pruned]:
                    for k in self.prune_keys:
                        if k in e:
                            del e[k]
                    pruned.append(e)
                else:
                    print 'prune:', e[keys.entity_profile]
            except Exception as ex:
                print 'prune exception:', ex, e
                exit() 
        return pruned
    
    def get_common_name(self):
        return self.__class__.__name__.lower()
    
    def error_league(self, err):
        print 'error league:', self.get_common_name(), err

    def pretty_print(self, p):
        pprint.pprint(p)
        return p
    
    def process_entities(self, pretty = False, exit_on_complete = False):
        print 'process_entities'
        d = self.entities()        
        if pretty:
            d.addCallback(self.pretty_print)
        if exit_on_complete:
            d.addCallback(lambda ign: reactor.stop())
        return d

class SharedLeague(Common):
    
    shared_font = '/script/font/Roboto-Regular.ttf?raw=true'
    
    wikipedia = 'https://en.wikipedia.org/wiki'
    relationship_keys = [keys.entity_site, keys.entity_league, keys.entity_profile]         
    min_size = 1
    max_size = 5000
    save_db = True
    
    def add_twitter_ignore(self, ignore_twitter):
        print 'twitter ignore:', ignore_twitter
        po = self.get_twitter_ignores()
        po.append(ignore_twitter)
        s3.save_s3(
            s3.bucket_straight(User().get_curator(self.get_league_name())[user_keys.user_role]),
            '/' + self.get_league_name() + '/twitter_ignores.json',
            json.dumps(po),
            None,
            content_type='application/json',
            acl='public-read'
        )
        print 'done save'
        del self.twitter_ignores

    def get_twitter_ignores(self):
        if hasattr(self, 'twitter_ignores'):
            return self.twitter_ignores
        else:
            try:
                site_value = User().get_curator(self.get_league_name())[user_keys.user_role]
                key_value = '/' + self.get_league_name() + '/twitter_ignores.json'
                print 'site:', site_value, 'key value:', key_value
                ti = s3.bucket_straight(site_value).lookup(key_value).get_contents_as_string()
                self.twitter_ignores = json.loads(ti)
            except Exception as e:
                print e
                self.twitter_ignores = []
        return self.twitter_ignores

    def get_league_name(self):
        return self.__class__.__name__.lower()
                
    def player_delta(self, scraped_player, existing_player):
        different = {}
        union_keys = set(scraped_player.keys() + existing_player.keys())
        compare_keys = [uk for uk in union_keys if uk not in self.relationship_keys and uk not in keys.social_keys and not uk.startswith('ts_') and not uk == self.get_league_name() + '_blocks'] 
        for key in compare_keys:                        
            if (key not in scraped_player.keys() or not scraped_player[key]) and (key not in existing_player.keys() or not existing_player[key]):
                pass
            elif (key not in scraped_player.keys() or not scraped_player[key]) and (key in existing_player.keys() and existing_player[key]):
                different[key + '__remove'] = existing_player[key]
                del existing_player[key]
            elif (key in scraped_player.keys() and scraped_player[key]) and (key not in existing_player.keys() or not existing_player[key]):
                different[key + '__add'] = scraped_player[key]
                existing_player[key] = scraped_player[key]
            elif existing_player[key] != scraped_player[key]:
                if simplejson.dumps(existing_player[key]) != simplejson.dumps(scraped_player[key]):
                    different[key + '__change'] = '__'.join([simplejson.dumps(existing_player[key]).replace('"',''), simplejson.dumps(scraped_player[key]).replace('"','')])
                    existing_player[key] = scraped_player[key]
        return different                    
                    
    def name_collision(self, league_name, entity_profile, entity_name):
        name_collisions = []
        for np in Entity().query_2(league__eq=league_name, query_filter={'name__eq': entity_name, 'profile__ne':entity_profile}, conditional_operator='AND'):
            print 'found name collision:', np._data[keys.entity_name], entity_profile
            name_collisions.append(np)                    
        return name_collisions        
    
    def drop_prevented(self, entity):
        print 'drop_prevented:', entity[keys.entity_profile]
      
    def process_drop(self, existing_player, curator, league):
        ct = tweets.cut_tweet(existing_player._data, curator, league)
        try:
            print 'cut tweet:', ct
        except:
            pass
        EntityHistory().cut(league[keys.entity_league], existing_player)                                    
        message = {}
        message.update(existing_player._data)                                
        message[twitter_keys.message_tweet] = ct
        return message
                                             
    def process_delta(self, scraped_player, existing_player, differences, curator, league):
        print 'not dry run-', existing_player[keys.entity_league]
        scraped_player[keys.entity_league] = existing_player[keys.entity_league]
        scraped_player[keys.entity_site] = curator[user_keys.user_role]
        message = {}
        message.update(existing_player._data)
        message.update(scraped_player)
        message.update(differences)
        for key in [k for k in existing_player.keys() if k.startswith('ts_')] + keys.social_keys + [k for k in existing_player.keys() if k.startswith('ct_')]:
            scraped_player[key] = existing_player[key]                                    
        overwrite = Entity().put_item(scraped_player, overwrite=True)
        print 'overwrite:', overwrite
        try:
            put_result = EntityHistory().delta(existing_player, differences)
            print 'difference tweet:', put_result
        except Exception as e:
            print 'difference exception:', e        
        dt = tweets.delta_tweet(scraped_player, existing_player, differences, curator, league)
        try:
            print 'delta tweet:', dt
        except:
            pass
        try:
            message[twitter_keys.message_tweet] = dt
            #if not self.filter_tweet(message):
            #    TweetQueue().createMessage(message)
            return message
        except Exception as e:
            print 'delta tweet exception:', e             

    def filter_tweet(self, msg):
        if 'rank__change' in msg:
            rank_from = int(msg['rank__change'].split('__')[0])
            rank_to = int(msg['rank__change'].split('__')[1])
            return rank_to > rank_from - self.rank_difference_filter 
        print 'should override'
        return False
    
    def check_existing_players(self, existing_players, players, curator, league):
        updates = []
        drops = []        
        for p in existing_players:                 
            try:
                scraped_player = [player for player in players if player[keys.entity_profile] == p[keys.entity_profile]][0]                    
                differences = self.player_delta(scraped_player, p)             
                if differences:
                    updates.append((scraped_player, p, differences))
            except IndexError:                
                drops.append(p)
            except Exception as e:
                print 'process_existing_players exception:', e        
        return (updates, drops)

    def process_add(self, new_player, curator, league):        
        print 'try to find old cut-', curator[user_keys.user_role], league[keys.entity_league]
        history_last_cut = EntityHistory().last_cut(new_player[keys.entity_profile], league[keys.entity_league])
        if history_last_cut: 
            print 'found cut instance:', fixed.lingo_since(history_last_cut, time_keys.ts_cut)
            for key in [k for k in history_last_cut.keys() if k in keys.social_keys]:
                if history_last_cut[key] and key != keys.entity_match_twitter:                                                    
                    print 'cut player with key:', key, 'adding to new player:', history_last_cut[key]
                    if key == keys.entity_twitter_id:
                        new_player[key] = str(history_last_cut[key])
                    else:
                        new_player[key] = history_last_cut[key]
        else:
            print 'never been cut'
        
        new_player[keys.entity_league] = league[keys.entity_league]
        new_player[keys.entity_site] = curator[user_keys.user_role]
        print new_player
        try: 
            Entity().put_item(new_player)
            addtweet = tweets.add_tweet(new_player, curator, league)
            try:                            
                print 'add tweet:', addtweet
            except:
                pass
            message = {}
            message.update(new_player)
            message[twitter_keys.message_tweet] = addtweet
            return message            
        except Exception as e:
            print 'already exists:', e            

    def league_compare(self, no_drops=False, dry_run=False):
        league = Entity().get_league(self.get_league_name())
        curator = User().get_curator(league[keys.entity_league])
        redirect = s3.get_redirect(s3.bucket_straight(curator[user_keys.user_role]), league[keys.entity_league] + '/db/league.json') 
        key = s3.check_key(s3.bucket_straight(curator[user_keys.user_role]), redirect)                
        print 'redirect:', redirect, 'key:', key, 'meta:', key.metadata        
        if time_keys.ts_compare not in key:
            entities = []
            loaded_entities = json.loads(key.get_contents_as_string())
            for le in loaded_entities:
                if le[keys.entity_profile] not in [e for e in entities]:
                    entities.append(le)
                else:
                    print 'entity exists:', le[keys.entity_profile]
            print 'entities:', len(entities)        
            self.entities_league_compare(entities, curator, league, no_drops, dry_run, key)            
        
    def entities_league_compare(self, players, curator, league, no_drops=True, dry_run=True, import_key=None):
        try:
            existing_players = [p for p in Entity().query_2(league__eq=league[keys.entity_league], profile__beginswith='http:')]
            existing_profile_list = [ep[keys.entity_profile] for ep in existing_players]        
            scraped_new_players = [p for p in players if p[keys.entity_profile] not in existing_profile_list]
            pd = float(abs(len(existing_players) - len(players)))/float(max(len(existing_players), len(players))) * 100
            print 'percentage difference:', pd 
            updates, drops = self.check_existing_players(existing_players, players, curator, league)
            self.derived_entities(players)             
            if not dry_run:
                tweets = []
                for sp, ep, d in updates:
                    try:
                        delta_tweet = self.process_delta(sp, ep, d, curator, league)
                        tweets.append(delta_tweet)
                    except Exception as e:
                        print 'delta exception:', e
                user_no_drops = True
                try:
                    u = User().get_by_role(league[keys.entity_league], keys.entity_twitter)
                    user_no_drops = fixed.no_drops(u)
                except:
                    print 'missing user:', league[keys.entity_league]
                print 'user_no_drops:', user_no_drops, 'no_drops:', no_drops 
                for drop in drops:
                    if not user_no_drops and not no_drops:
                        drop_tweet = self.process_drop(drop, curator, league)
                        if drop_tweet: 
                            tweets.append(drop_tweet)             
                    elif no_drops:
                        print 'drops prevented by process:', drop[keys.entity_profile]
                        self.drop_prevented(drop)              
                    else:
                        print 'drop prevent by league:', drop[keys.entity_profile]
                        self.drop_prevented(drop)
                for np in scraped_new_players:
                    add_tweet = self.process_add(np, curator, league)
                    if add_tweet: 
                        tweets.append(add_tweet)
                print 'tweets length:', len(tweets)                
                if import_key:                
                    sb = s3.bucket_straight(curator[user_keys.user_role])
                    import_key.metadata.update({time_keys.ts_compare:int(time.time()), 'Content-Type': 'application/json'})
                    k2 = sb.copy_key(import_key.name, import_key.bucket.name, import_key.name[1:], metadata=import_key.metadata, preserve_acl=True)
                    k2.metadata = import_key.metadata
                    k2.set_metadata('Content-Type','application/json')
                    k2.make_public()
                    print k2, k2.metadata
            else:
                for d in drops:
                    print 'drop:', d[keys.entity_profile], d[keys.entity_name] if keys.entity_name in d else 'No Name', d[keys.entity_twitter] if keys.entity_twitter in d else 'No Twitter'
                for u in updates:
                    print 'update:', u[0][keys.entity_profile], u[0][keys.entity_name].encode('utf-8') if keys.entity_name in u[0] else 'No Name', u[1][keys.entity_twitter] if keys.entity_twitter in u[1] else 'No Twitter', u[2].keys()
                for n in scraped_new_players:
                    print 'add:', n[keys.entity_profile], n[keys.entity_name] if keys.entity_name in n else 'No Name'
        except Exception as e:
            print 'compare exception:', e
        
        print 'congrats done'            

    def entities(self):
        print 'no entities - should'
        return defer.succeed([])
    
    def entity_error(self, err):
        print 'entity_error:', err    
        
    def derived_entities(self, players):
        print 'derived_entities should overwrite'
        pass

    def process_league(self, exit_on_complete = True):
        print 'league name:', self.get_league_name()
        d = self.process_inline()
        if exit_on_complete:
            d.addCallback(lambda ign: reactor.stop())
        return d
    
    @defer.inlineCallbacks 
    def process_inline(self):            
        raw_entities = yield self.entities()                 
        print 'raw entities:', len(raw_entities)            
        all_entities = self.prune_dups(raw_entities)
        if len(all_entities) >= self.min_size and len(all_entities) <= self.max_size and self.save_db:
            print 'accpetable entities', len(all_entities)
            try:           
                io = json.dumps(all_entities, cls=fixed.SetEncoder)
                bucket = s3.bucket_straight(User().get_curator(self.get_league_name())[user_keys.user_role])
                db_count = '1'
                try:
                    redirect = s3.get_redirect(bucket, '/' + self.get_league_name() + '/db/league.json')
                    db_count = str(int(redirect[len('/' + self.get_league_name() + '/db/league'):][:-5]) + 1)
                except Exception as e:
                    print 'db count redirecct exception:', 3
                    try:
                        index = 0
                        for key in bucket.list(prefix=self.get_league_name() + '/db/league'):
                            index += 1
                        db_count = str(index)                            
                    except:
                        print 'db count prefix exception!'        
                locate = '/' + self.get_league_name() + '/db/league' + db_count + '.json'
                ts_scraped = int(time.time())
                bible_tweet = { time_keys.ts_scraped: ts_scraped, keys.entity_count: len(all_entities) }
                league_for_message = Entity().get_league(self.get_league_name())
                bible_tweet.update(league_for_message._data)
                bible_tweet[twitter_keys.message_tweet] = tweets.bible_tweet(User().get_curator(self.get_league_name()), league_for_message)
                
                print locate, bible_tweet
                s3.save_s3(bucket, locate , io, None, 'application/json', 'public-read', bible_tweet)
                s3.create_local_redirect(bucket, self.get_league_name() + '/db/league.json', locate)
                
                league_user = User().get_by_role(self.get_league_name(), keys.entity_twitter)
                league_user_app = auth.user_app(league_user)
                if league_user_app:
                    if not restful.post_tweet(league_user, league_user_app, bible_tweet[twitter_keys.message_tweet]):
                        TweetQueue().createMessage(bible_tweet)
                else:
                    TweetQueue().createMessage(bible_tweet)                    
                try:
                    user_league = User().get_by_role(self.get_league_name(), keys.entity_twitter)
                    user_league[time_keys.ts_bible] = ts_scraped
                    user_league.partial_save()
                except:
                    print 'missing user:', self.get_league_name()
                print 'league done:', self.get_league_name(), 'all entities length:', len(all_entities)
                defer.returnValue(True)
            except Exception as e:
                print 'except:', e            
                
class TeamSportsLeague(SharedLeague):
    
    can_have_empty_teams = False
    create_missing_teams = True
    remove_lost_teams = False
    
    def teams_to_players(self, teams):
        players = []
        print 'length of teams:', len(teams)
        for team in teams:
            print 'length of players:', len(team['players']), team[keys.entity_team]
            if len(team['players']) == 0 and not self.can_have_empty_teams:
                print 'zero players on team:', team[keys.entity_team]
                reactor.stop()
            for p in team['players']:
                p[keys.entity_team] = team[keys.entity_team]
                if p[keys.entity_profile] not in [p2[keys.entity_profile] for p2 in players]:
                    players.append(p)
                else:
                    print 'duplicate?:', p[keys.entity_profile]
        print 'length of players:', len(players)
        return players    
    
    def derived_entities(self, players):
        derived_team_names = []
        missing_team = []        
        found_team = []
        lost_team = []
        for p in players:
            if keys.entity_team in p and p[keys.entity_team] not in derived_team_names:
                derived_team_names.append(p[keys.entity_team])
        for team_name in derived_team_names:
            try:
                team_entity = Entity().get_item(league=self.get_league_name(), profile=Entity().team_profile(team_name))
                print 'found team:', fixed.team_name(team_entity)
                found_team.append(team_entity)
                #players.append(team_entity)
            except Exception as e:
                missing_team.append(team_name)
                print 'derived missing team:', team_name, self.get_league_name(), e
                if self.create_missing_teams:
                    Entity().put_item(data={keys.entity_league: self.get_league_name(), keys.entity_profile: Entity().team_profile(team_name), keys.entity_site: User().get_curator(self.get_league_name())[user_keys.user_role] })
        for e in Entity().query_2(league__eq=self.get_league_name(),profile__beginswith='team:'):
            if e[keys.entity_profile] not in [ft[keys.entity_profile] for ft in found_team]:
                print 'lost team:', fixed.team_name(e) 
                lost_team.append(e)
                if self.remove_lost_teams:
                    e.delete()
        print 'derived_team_names:', len(derived_team_names), 'missing_team:', len(missing_team), 'found team:', len(found_team), 'lost team:', len(lost_team)        

class TMSportsLeague(TeamSportsLeague):

    @defer.inlineCallbacks
    def transfermarket(self, cv):   
        teams = []
        for division_seq in self.divisions:
            print 'division href:', division_seq[0]
            html = yield cv.goto_url(division_seq[0]).addCallback(cv.to_html)
            division_txt = division_seq[1]
            print 'division text:', division_txt
            for div in html.cssselect('div.table-header'):
                print 'header text:', parse.csstext(div)
                if division_txt in parse.csstext(div):                    
                    trs = div.getparent().cssselect('div.responsive-table div.grid-view[id=yw1] table.items tr')
                    for tr in trs[2:]:
                        teams.append({'href': 'http://www.transfermarkt.com' + tr[1][0].attrib['href']})
            for team in teams:
                print 'team href:', team['href']
                team['players'] = []
                #print '    ', team['href']
                team_html = yield cv.goto_url(team['href']).addCallback(cv.to_html)
                #<meta property="og:title" content="Paris Saint-Germain - Club's profile ">
                tn = team_html.cssselect('meta[property="og:title"][content]')[0].attrib['content'].split(' - Club')[0]
                team[keys.entity_profile] = 'team:' + tn
                team[keys.entity_team] = tn.strip()
                for tr in team_html.cssselect('div.box div.responsive-table div.grid-view[id=yw1] table.items tr')[1:]:
                    try:               
                        player = {}
                        player[keys.entity_jersey] = parse.csstext(tr[0])
                        if len(tr[1]) == 3:
                            row = tr[1][2]
                        else:
                            row = tr[1][0]                            
                        p_a = row[0][0][1][0][0][0]                        
                        profile = 'http://www.transfermarkt.com' + p_a.attrib['href']
                        player[keys.entity_profile] = profile
                        player[keys.entity_name] = parse.csstext(p_a)
                        player[keys.entity_position] = parse.csstext(row[0][1][0])
                        age_birth = parse.csstext(tr[3])
                        player[keys.entity_age] = age_birth.split('(')[1].split(')')[0]
                        player[keys.entity_dob] = age_birth.split('(')[0].strip()
                        nationality = tr[4].cssselect('img.flaggenrahmen')
                        if len(nationality) == 1:
                            player[keys.entity_origin] = nationality[0].attrib['title']
                        elif len(nationality) == 2:
                            player[keys.entity_nationality] = nationality[1].attrib['title']
                            player[keys.entity_origin] = nationality[0].attrib['title']
                        team['players'].append(player)                    
                    except:
                        pass
                print '    ', tn, len(team['players'])
        print 'done with:', division_txt
        all_players = self.teams_to_players(teams)
        print len(all_players)
        defer.returnValue(all_players)           

class SportsLeague(SharedLeague):
    
    pass