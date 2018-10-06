from app import user_keys

from amazon.dynamo import User

from twitter import auth

for i, l in enumerate(User().get_leagues()):
    locked = False
    if l[user_keys.user_locked]:
        locked = True
    app_name = None
    ua = auth.user_app(l)
    if ua:
        app_name = ua[user_keys.user_twitter_apps].keys()[0]
    print '{:3s}'.format(str(i+1)), '{:6s}'.format(str(locked)), '{:20s}'.format(l[user_keys.user_role]), '{:40s}'.format(str(app_name))