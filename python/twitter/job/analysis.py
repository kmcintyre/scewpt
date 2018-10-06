from app import fixed, keys, time_keys, user_keys

from twitter import twitter_keys

from amazon.dynamo import Entity, ProfileTwitter, User
from amazon.sqs import StalkQueue
from amazon import s3
import sys

import simplejson as json
from league.services import shared

def stalk_analysis(league_name):        
    mutuals = []
    extras = []
    for mf in Entity().query_2(league__eq=league_name):
        if 'twitter' in mf and 'ts_followers_' + league_name in mf:
            try:
                ts_add = None
                if mf[time_keys.ts_scout]:
                    ts_add = mf[time_keys.ts_scout]
                slt = ProfileTwitter().profile_last(mf[keys.entity_twitter_id], None, ts_add) 
                if slt is not None:
                    print 'append:', mf[keys.entity_twitter], 'since:', fixed.lingo_since_date(ts_add)                
                    mutuals.append( (mf, slt) )
                else:
                    print 'no last stats:', mf[keys.entity_twitter], mf[keys.entity_twitter_id]
            except Exception as e:
                print 'missing:', e, 'https://twitter.com/' + mf[keys.entity_twitter], fixed.lingo_since(mf, twitter_keys.league_ts_followers(league_name))
        else:
            extras.append(mf._data)
    print 'extras length:', len(extras)
    for mutual_seq in mutuals:
        try:
            mutual = mutual_seq[0]
            mutual_slt = mutual_seq[1]
            print 'mutual:', mutual[keys.entity_twitter]
            tf = set([])            
            for other_seq in [others for others in mutuals if others[0] != mutual and twitter_keys.league_mutual(league_name) in others[1]]:
                if mutual[keys.entity_twitter_id] in other_seq[1][twitter_keys.league_mutual(league_name)]:
                    tf.add(other_seq[0][keys.entity_twitter_id])
            if len(tf) > 0:
                print mutual[keys.entity_twitter], 'follows:', len(tf), 'following:', 0 if twitter_keys.league_mutual(league_name) not in mutual_slt else len(mutual_slt[twitter_keys.league_mutual(league_name)])
                mutual_slt[twitter_keys.league_follows(league_name)] = tf
                mutual_slt.partial_save()                          
            else:
                print 'not following anyone:', mutual[keys.entity_twitter], mutual[keys.entity_twitter_id]
        except Exception as e:
            print 'mutual exception:', e
    publish = []
    curator = User().get_curator(league_name)
    for mutual_seq_2 in mutuals:
        try:
            p = {}
            mutual = mutual_seq_2[0]
            p.update(mutual._data)
            mutual_slt = mutual_seq_2[1]
            p.update(mutual_slt._data)
            publish.append(p)
        except:
            print 'mutual exception:', e
    b = s3.bucket_straight(curator[user_keys.user_role])
    filename = league_name + '/db/bible.json'
    meta = shared.entity_filter(curator._data)
    output = shared.dump(publish + extras)
    s3.save_s3(b, filename, output , None, content_type='application/json', acl='public-read', meta=meta, encode='gzip')    

def check_stalk_queue():
        
    sq = StalkQueue()
    print 'check stalk queue:', sq    
    try:
        msg = sq.getMessage()
        if msg:        
            stalk = json.loads(msg.get_body())
            print 'stalk msg:', stalk
            stalk_analysis(stalk[keys.entity_league])
            print 'delete stalk msg!'
            sq.deleteMessage(msg)
    except Exception as e:            
        print 'stalk exception:', e
            
if __name__ == '__main__':
    if len(sys.argv) > 1:
        stalk_analysis(sys.argv[1]) 
    else:
        check_stalk_queue()