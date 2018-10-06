from app import keys, user_keys
from app import fixed
from twitter import twitter_keys

def delta(differences):
    change_suffix = []
    def add_suffix(suffix):
        if change_suffix:
            prev = (',')
            suffix_index = 0
            while prev[0] == ',':
                suffix_index += -1
                prev = change_suffix[suffix_index]
            if prev[0] == suffix[0]:
                suffix[0] = ','             
        change_suffix.append(suffix)
    for ck, cv in [(dk, differences[dk]) for dk in differences.keys() if dk.split("__")[-1] == 'change']:
        nv = cv.split('__')[1]
        add_suffix([ck.split('__')[0], cv.split('__')[0], 'to', nv])
    for ck, cv in [(dk, differences[dk]) for dk in differences.keys() if dk.split("__")[-1] in ['remove', 'add']]:
        add_suffix([ck.split('__')[1], ck.split('__')[0], cv])
    return change_suffix

def id_instagram(id_player, curator, league):
    tweet = [curator[user_keys.user_role] + '/#' + league[keys.entity_league], 'ids']
    tweet.append(fixed.adjust_name(id_player))
    tweet.append('as')    
    tweet.append('https://www.instagram.com/' + id_player[keys.entity_instagram])
    if id_player[keys.entity_profile].startswith('http'):             
        tweet.extend(['via', id_player[keys.entity_profile]])
    else:
        tweet.extend(['via', id_player[keys.entity_profile].split(':', 1)[1]])
    tweet.extend(twitter_keys.bio_hash(id_player, league))
    return u' '.join(tweet)

def id_facebook(id_player, curator, league):
    tweet = [curator[user_keys.user_role] + '/#' + league[keys.entity_league], 'ids']
    tweet.append(fixed.adjust_name(id_player))
    tweet.append('as')    
    tweet.append('https://www.facebook.com/' + id_player[keys.entity_facebook])
    if id_player[keys.entity_profile].startswith('http'):             
        tweet.extend(['via', id_player[keys.entity_profile]])
    else:
        tweet.extend(['via', id_player[keys.entity_profile].split(':', 1)[1]])
    tweet.extend(twitter_keys.bio_hash(id_player, league))
    return u' '.join(tweet)

def id_twitter(id_player, curator, league):
    tweet = [curator[user_keys.user_role] + '/#' + league[keys.entity_league], 'ids']
    tweet.append(fixed.adjust_name(id_player))
    tweet.append('as')    
    tweet.append('#' + id_player[keys.entity_twitter])
    if id_player[keys.entity_profile].startswith('http'):             
        tweet.extend(['via', id_player[keys.entity_profile]])
    else:
        tweet.extend(['via', id_player[keys.entity_profile].split(':', 1)[1]])
    tweet.extend(twitter_keys.bio_hash(id_player, league))
    return u' '.join(tweet)

def chart_tweet(curator, title):
    tweet = [curator[user_keys.user_role], 'renders', '{0}' + title + '{1}']    
    tweet.extend(['tracking', str(curator[keys.count(keys.entity_twitter)])])
    tweet.extend(['entities', '#DataIsBeautiful', '#Charts', '#Analytics'])
    t = u' '.join(tweet).format(u"\u201C", u"\u201D")
    return t.encode('utf-8') 

def add_tweet(add_player, curator, league):
    tweet = [curator[user_keys.user_role] + '/#' + league[keys.entity_league], 'adds']
    tweet.append(fixed.adjust_name(add_player))
    #if keys.entity_twitter in add_player:
    #    tweet.append('@' + add_player[keys.entity_twitter])    
    if add_player[keys.entity_profile].startswith('http://'):
        tweet.extend(['via', add_player[keys.entity_profile]])
    tweet.extend(twitter_keys.bio_hash(add_player, league))
    return u' '.join(tweet)

def bible_tweet(curator, league):
    tweet = [curator[user_keys.user_role] + '/#' + league['league'], 'releases', curator[user_keys.user_role] + '/' + league['league'] + '/db/league.json', '#BigData', 'powering website - available daily', '#CloudComputing']
    tweet.extend(twitter_keys.bio_hash(curator, league))    
    return u' '.join(tweet)

def cut_tweet(cut_player, curator, league):
    tweet = [curator[user_keys.user_role] + '/#' + league[keys.entity_league], 'drops']
    tweet.append(fixed.adjust_name(cut_player))
    #if keys.entity_twitter in cut_player:
    #    tweet.append('@' + cut_player[keys.entity_twitter])        
    tweet.append(cut_player[keys.entity_profile])
    tweet.append('#BestOfLuck')
    tweet.extend(twitter_keys.bio_hash(cut_player, league))
    return u' '.join(tweet)

def delta_tweet(delta_player, existing_player, differences, curator, league):
    try:
        tweet = [curator[user_keys.user_role] + '/#' + league[keys.entity_league], 'updates']
        if keys.entity_twitter in delta_player and delta_player[keys.entity_twitter]:
            tweet.append(fixed.adjust_name(delta_player))
            #tweet.append('@' + delta_player[keys.entity_twitter])
        elif keys.entity_twitter in existing_player and existing_player[keys.entity_twitter]:
            tweet.append(fixed.adjust_name(existing_player))
        else:            
            tweet.append(fixed.adjust_name(delta_player))
        tweet.append(delta_player[keys.entity_profile])
        change_suffix = delta(differences)
        tweet.append(u' '.join([u' '.join(c) for c in change_suffix]).replace('  ', ' ').replace(' ,', ','))
        if len(differences.keys()) == 1 and differences.keys()[0] == 'age__change' and int(differences['age__change'].split('__')[0]) + 1 == int(differences['age__change'].split('__')[1]):
            tweet.append('#HappyBirthday')
        if keys.entity_twitter in delta_player:
            tweet.extend(twitter_keys.bio_hash(delta_player, league))
        return u' '.join(tweet)
    except Exception as e:
        print 'delta tweet exception:', e, delta_player, existing_player, differences
        return ''

def avi_tweet(curator, league, entity, count):
    tweet = [curator[user_keys.user_role] + '/#' + league[keys.entity_league], 'updates', 'avi', '#' + str(count)]
    tweet.append(curator[user_keys.user_role] + '/tw/' + entity[keys.entity_twitter_id] + '/avatar_large.png')
    tweet.append('for')
    tweet.append(fixed.adjust_name(entity))
    #if entity[keys.entity_twitter]:
    #    tweet.append('@' + entity[keys.entity_twitter])
    tweet.extend(twitter_keys.bio_hash(entity, league))
    return u' '.join(tweet)

def bg_tweet(curator, league, entity, count):
    tweet = [curator[user_keys.user_role] + '/#' + league[keys.entity_league],'updates', 'background-image', '#' + str(count)]
    tweet.append(curator[user_keys.user_role] + '/tw/' + entity[keys.entity_twitter_id] + '/background.png')
    tweet.append('for')
    tweet.append(fixed.adjust_name(entity))
    #if entity[keys.entity_twitter]:
    #    tweet.append('@' + entity[keys.entity_twitter])    
    tweet.extend(twitter_keys.bio_hash(entity, league))
    return u' '.join(tweet)

def card_tweet(curator, league, entity, count):
    tweet = [curator[user_keys.user_role] + '/#' + league[keys.entity_league],
             'updates', 'card', '#' + str(count)]
    tweet.append(curator[
                 user_keys.user_role] + '/tw/' + entity[keys.entity_twitter_id] + '/card.png')
    tweet.append('for')
    tweet.append(fixed.adjust_name(entity))
    #if entity[keys.entity_twitter]:
    #    tweet.append('@' + entity[keys.entity_twitter])    
    tweet.extend(twitter_keys.bio_hash(entity, league))
    return u' '.join(tweet)


def league_scouting_report(league_name):
    from amazon.dynamo import Entity, User
    s1 = '%s %s' % (Entity().query_count(league__eq=league_name, profile__beginswith='team:'), 'Teams')
    s2 = '%s %s' % (Entity().query_count(league__eq=league_name, profile__beginswith='http:'), 'Players')
    s3 = '%s %s' % (Entity().query_count(index=Entity.index_twitter, league__eq=league_name), 'Tweeter(s)')
    # s4 = time.strftime("%a, %d %H:%M", time.localtime())
    announce = u' '.join([User().get_curator(league_name)[user_keys.user_role] + '/#' + league_name, 'curates', league_name, 'with', s1, s2, s3])
    return announce    
