import sys

from app import keys, time_keys, user_keys
from app import fixed

from twitter import auth, restful

from amazon.dynamo import User
from amazon.sqs import StalkQueue

def inflate_service(perform = False):
    
    users = []
    for t in [User]:
        for u in t().scan():
            if u[user_keys.user_twitter_auth] and '.com' not in u[user_keys.user_role] and user_keys.user_locked not in u.keys():
                ua = auth.user_app(u)
                if ua: 
                    users.append(u)
    sorted_users = sorted(users, key=lambda item: item[time_keys.ts_inflated])
    for i, so in enumerate(sorted_users):
        print '{:3s}'.format(str(i+1)), '{:20s}'.format(so[user_keys.user_role]), fixed.lingo_since_date(so[time_keys.ts_inflated]), so.table.table_name
    
    if perform:    
        inflate_user = sorted_users[0]
        inflate_app_user = auth.user_app(inflate_user)         
        
        print ''
        print inflate_user[user_keys.user_role], inflate_app_user[user_keys.user_role], inflate_user.table.table_name
        restful.Inflate().do_inflate(inflate_user, inflate_app_user)
        StalkQueue().createMessage({keys.entity_league: inflate_user[user_keys.user_role]})

if __name__ == '__main__':    
    try:
        backup = bool(sys.argv[2])
    except:
        backup = False
    #if backup:
    #    t = UserAvailable
    #else:
    t = User                
    if len(sys.argv) > 1:
        if sys.argv[1] != 'True': 
            inflate_user = t().get_by_role(sys.argv[1], keys.entity_twitter)             
            print 'inflate:', inflate_user[user_keys.user_role], 'twitter:', inflate_user[keys.entity_twitter]  
            inflate_user_app = auth.user_app(inflate_user)
            app_name = inflate_user_app[user_keys.user_twitter_apps].keys()[0]    
            print 'app name:', app_name 
            if inflate_user[user_keys.user_twitter_auth] and app_name in inflate_user[user_keys.user_twitter_auth]:
                restful.Inflate().do_inflate(inflate_user, inflate_user_app)
            else:
                print 'no auth for app_name:', app_name
        else:
            inflate_service(True)
    else:
        inflate_service()