from amazon.dynamo import Tweet, ProfileTwitter
from twitter import twitter_keys
from instagram import instagram_keys
import time
import pprint

all_keys = [u'_ts_ms', u'_tweet_id', u'_twitter_id', u'abbrv', u'age', u'alexa_rank', u'appearances', u'assists', u'assumed_office', u'average', u'batch', u'bats', u'born', u'bracelets', u'captain', u'carlogo', u'carnumber', u'carries', u'cashes', u'ceo', u'circuit', u'circulating_supply', u'class', u'college', u'colors', u'company', u'competitors', u'continent', u'country', u'crunchbase', u'crunchbase_follower_count', u'crunchbase_followers', u'curator_site', u'deals', u'designation', u'division', u'dnf', u'dob', u'earnings', u'entity_count', u'established', u'experience', u'facebook', u'field_goals_attempted', u'field_goals_made', u'filings', u'firm', u'firstadded', u'flag', u'followers', u'following', u'forced_fumbles', u'foreign', u'founders', u'funding', u'games', u'games_started', u'gender', u'goals', u'google', u'headquarters', u'height', u'high_school', u'incubator', u'index', u'industry', u'inside_20', u'instagram', u'instagram_avi', u'instagram_id', u'instagram_name', u'instagram_url', u'instagram_verified', u'instagrams', u'interceptions', u'international', u'investments', u'investors', u'is_monologue', u'jersey', u'jersey_pic', u'known_conversation', u'known_instagrams', u'known_mentions', u'known_quote', u'known_retweet', u'last_valuation', u'league', u'line', u'linkedin', u'location', u'logo_external', u'long', u'market_cap', u'matches', u'mission', u'name', u'nationality', u'nickname', u'noted', u'noted_profile', u'origin', u'party', u'percentage', u'pic', u'points', u'points_behind', u'position', u'position_alt', u'post', u'posts', u'price', u'prior_exp', u'prize_money', u'prizemoney', u'profile', u'punts', u'rank', u'rating', u'ratio', u'reach', u'receptions', u'record', u'reds', u'resides', u'rings', u'roster_url', u'rounds', u'runs', u'sacks', u'salary', u'schedule', u'sector', u'self_instagrams', u'shoots', u'site', u'social_ts_received', u'source_instagram', u'source_twitter', u'sponsors', u'starts', u'state', u'status', u'style', u'summary', u'surface', u'symbol', u'tackles', u'team', u'team_href', u'term_expires', u'throws', u'titleholder', u'top10', u'top5', u'topic', u'total_funding', u'touchdowns', u'town', u'ts_add', u'ts_avatar', u'ts_backup', u'ts_delta', u'ts_following', u'ts_match_twitter', u'ts_retweet', u'ts_scout', u'ts_tweet', u'twitter', u'unknown_instagrams', u'unknown_quote', u'unknown_retweet', u'valuation', u'version', u'video_views', u'videos', u'website', u'week', u'weight', u'weightclass', u'wickets', u'wikipedia', u'wins', u'yards', u'yellows']

remove_keys = ['abbrv', 'alexa_rank', 'crunchbase_follower_count', 'crunchbase_followers', 
               'curator_site', 'entity_count', 'position_alt', 'social_ts_received', 
               'source_instagram', 'source_twitter', 'team_href', 'ts_add', 'ts_avatar', 'ts_backup', 
               'ts_delta', 'ts_following', 'ts_match_twitter', 'ts_retweet', 
               'ts_tweet', 'roster_url', 'version',
               twitter_keys.match_posts,
               twitter_keys.match_followers,
               instagram_keys.instagram_avi, 
               ProfileTwitter.following,
               instagram_keys.instagram_url,
               instagram_keys.instagram_verified               
               ]
update_keys = {'prize_money': 'prizemoney'}

kwargs = {}
for k in remove_keys + update_keys.keys():
    kwargs[k + '__null'] = False
kwargs['attributes'] = [Tweet.tweet_id, Tweet.tweet_user_id] + remove_keys + update_keys.keys()
kwargs['conditional_operator'] = 'OR'

for e in Tweet().scan(**kwargs):
    for k in remove_keys:
        if e[k]:
            del e[k]
    for k in update_keys.keys():
        if e[k]:
            e[update_keys[k]] = e[k]
    try:
        e.partial_save()
        pprint.pprint(e._data)
        time.sleep(.2)
    except:
        pass