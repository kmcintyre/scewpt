from amazon.dynamo import User, Entity
from twitter import restful, auth
from app import keys, user_keys

total_adds = 0

def get_list_id(list_name, lists):
    try:
        return [l['id'] for l in lists if l['name'] == list_name][0]
    except Exception as e:
        return None

def make_list_name(name):
    if name[:1].isdigit():
        return make_list_name(name.split(' ', 1)[1])
    elif len(name) < 26:
        return name
    else:
        return make_list_name(name.rsplit(' ', 1)[0])

def check_twitter(entity, add_members, existing_members):
    if entity[keys.entity_twitter] in existing_members:
        existing_members.remove(entity[keys.entity_twitter])
    else:
        add_members.append(entity[keys.entity_twitter])
        
def do_add_members(list_user, curator_user, list_id, add_members, oauth):
    global total_adds
    total_adds += len(add_members)
    if total_adds > 500:
        print 'total adds exit:', total_adds
        return False
    print 'total adds:', total_adds
    restful.list_add_members(list_user, curator_user, list_id, add_members, oauth)
    return True
    
def do_remove_members(list_user, curator_user, list_id, remove_members, oauth):
    global total_adds
    total_adds += len(remove_members)
    if total_adds > 500:
        print 'total adds exit:', total_adds
        exit()
    print 'total adds:', total_adds
    restful.list_remove_members(list_user, curator_user, list_id, remove_members, oauth)

def curator_lists(curator_name, league_name, do_add = True):
    print 'curator list:', curator_name, 'league:', league_name
    curator_user = User().get_by_role(curator_name, keys.entity_twitter)
    oauth = auth.get_oauth(curator_user, curator_user, curator_user[user_keys.user_twitter_apps].keys()[0])
    lists = restful.get_lists(curator_user, curator_user, oauth)
    
    curator_user[user_keys.user_home_lists] = len(lists)
    curator_user.save()    
    
    u = User().get_by_role(league_name, keys.entity_twitter)
    list_name = make_list_name(u[keys.entity_name].replace(' ', '-').replace('/', '_'))
    if not get_list_id(list_name, lists):
        print 'missing list:', list_name
        restful.create_list(curator_user, curator_user, list_name, u[keys.entity_description], oauth)
    else:
        print curator_name, league_name, 'has:', list_name                
        list_id = get_list_id(list_name, lists)
        existing_members = restful.list_members(curator_user, curator_user, list_id, oauth)
        print 'existing members:', len(existing_members)
        if do_add:
            add_members = []
            for e in Entity().query_2(league__eq=league_name, query_filter={'twitter__null': False}):
                check_twitter(e, add_members, existing_members)
                if len(add_members) == 100:
                    if not do_add_members(curator_user, curator_user, list_id, add_members, oauth):
                        return
                    add_members = []        
            if len(add_members) > 0:
                if not do_add_members(curator_user, curator_user, list_id, add_members, oauth):
                    return        
            print 'excess members:', len(existing_members), existing_members
            remove_members = []
            for em in existing_members:
                remove_members.append(em)
                if len(remove_members) == 100:
                    do_remove_members(curator_user, curator_user, list_id, remove_members, oauth)        
                    remove_members = []
            if len(remove_members) > 0:
                do_remove_members(curator_user, curator_user, list_id, remove_members, oauth)        

def league_lists(league_name, do_add = True):
    print 'league list:', league_name   
    league_user =  User().get_by_role(league_name, keys.entity_twitter)
    league_user_app = auth.user_app(league_user)    
    oauth = auth.get_oauth(league_user, league_user_app, league_user_app[user_keys.user_twitter_apps].keys()[0])
    lists = restful.get_lists(league_user, league_user_app, oauth)
    print 'lists:', len(lists), [_l['name'] for _l in lists]
    league_user[user_keys.user_home_lists] = len(lists)
    league_user.save()    
    for team in Entity().query_2(league__eq=league_name, profile__beginswith='team:', reverse=True):
        team_name = make_list_name(team[keys.entity_profile].split(':')[1])
        if not get_list_id(team_name, lists):
            print 'missing list:', team_name
            list_description = u'Tracking {0} {1} from {2}'.format(league_user[keys.entity_name], league_user[keys.entity_lingo]['players'], team_name)
            restful.create_list(league_user, league_user_app, team_name, list_description, oauth)
        else:
            print league_name, 'has:', team_name
            list_id = get_list_id(team_name, lists) 
            existing_members = restful.list_members(league_user, league_user_app, list_id, oauth)
            print team_name, 'existing members:', len(existing_members)
            if do_add:
                add_members = []            
                for e in Entity().query_2(index=Entity.index_team_profile, team__eq=team[keys.entity_profile].split(':', 1)[1], query_filter={'twitter__null': False}):
                    check_twitter(e, add_members, existing_members)
                    if len(add_members) == 100:
                        if not do_add_members(league_user, league_user_app, list_id, add_members, oauth):
                            return
                        add_members = []
                if len(add_members) > 0:
                    if not do_add_members(league_user, league_user_app, list_id, add_members, oauth):
                        return                
                print 'excess members:', len(existing_members), existing_members
                remove_members = []
                for em in existing_members:
                    remove_members.append(em)
                    if len(remove_members) == 100:
                        do_remove_members(league_user, league_user_app, list_id, remove_members, oauth)        
                        remove_members = []
                if len(remove_members) > 0:
                    do_remove_members(league_user, league_user_app, list_id, remove_members, oauth)        
            
if __name__ == '__main__':
    import sys
    if '.com' in sys.argv[1]:
        da = True
        try:
            da = bool(sys.argv[3] != 'False')
        except:
            pass
        curator_lists(sys.argv[1], sys.argv[2], da)
        
    else:
        da = True
        try:
            da = bool(sys.argv[2] != 'False')
        except:
            pass
        league_lists(sys.argv[1], da)