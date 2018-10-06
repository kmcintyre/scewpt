from amazon.dynamo import Entity, User, ProfileTwitter

from app import keys, user_keys

from twitter import twitter_keys

def get_mutual(tp, ln):
    if not tp[twitter_keys.league_mutual(ln[user_keys.user_role])]:
        return 0
    else:
        return len(tp[twitter_keys.league_mutual(ln[user_keys.user_role])])
def get_follows(tp, ln):
    if not tp[twitter_keys.league_follows(ln[user_keys.user_role])]:
        return 0
    else:
        return len(tp[twitter_keys.league_follows(ln[user_keys.user_role])])
    
def unqualified(l):
    print 'unqualified:', 'https://twitter.com/' + l[keys.entity_twitter], l[keys.entity_profile] 

def do_process(ln, l, tp, dumping = False):
    mutual = get_mutual(tp, ln)
    follows = get_follows(tp, ln)
    is_qualified = True
    if not l[twitter_keys.league_blocks(ln[user_keys.user_role])] and not tp[ProfileTwitter.protected] and mutual < ln[user_keys.user_twitter_qualify]:
        is_qualified = False              
    try:
        print '{:15s}'.format(l[keys.entity_league]), '{:37s}'.format('https://twitter.com/' + l[keys.entity_twitter]), 'b:', l[twitter_keys.league_blocks(ln[user_keys.user_role])], 'p:', tp[ProfileTwitter.protected], 'm:', '{:3s}'.format(str(mutual)), 'f:', '{:3s}'.format(str(follows)), l[keys.entity_profile]
    except:
        pass    
        
    if not is_qualified:
        unqualified(l)
        '''
        if mutual == 0 and dumping:
            print 'dumping'
            for k in [keys.entity_twitter_id, keys.entity_twitter]:
                try:
                    del l[k]
                except:
                    pass
            for k in [ts for ts in l.keys() if ts.startswith('ts_')]:
                try:
                    del l[k]
                except:
                    pass
            l.partial_save()
        '''              

for ln in User().get_leagues():
    qualify = ln[user_keys.user_twitter_qualify]
    print ln[user_keys.user_role], 'qualify:', qualify
    print ''
    for l in Entity().query_2(league__eq=ln[user_keys.user_role], query_filter={'twitter__null':False}):
        try:
            if l[twitter_keys.league_blocks(ln[user_keys.user_role])] and not isinstance(l[twitter_keys.league_blocks(ln[user_keys.user_role])], bool):
                print 'set as boolean'
                l[twitter_keys.league_blocks(ln[user_keys.user_role])] = True
                l.partial_save()                
            tp = ProfileTwitter().profile_last(l[keys.entity_twitter_id])
            if tp:                
                do_process(ln, l, tp, True)
            else:
                print 'missing:', 'https://twitter.com/' + l[keys.entity_twitter], l[keys.entity_profile]
        except Exception as e:
            print 'exception:', e, l._data
            
