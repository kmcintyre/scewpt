from amazon.dynamo import User, Entity
from amazon import s3
from app import user_keys, keys
from urllib2 import urlopen
from wand.image import Image

for u in User().get_leagues():
    e = Entity().get_league(u[user_keys.user_role]) 
    bg = 'http://' + e[keys.entity_site] + '/tw/' + e[keys.entity_twitter_id] + '/background.png'
    try:
        f = urlopen(bg)
    except:
        f = urlopen('http://s3.amazonaws.com/scewpt.com/1500x500.png')
    with Image(file=f) as img:
        width = img.width
        height = img.height
        img.resize(300, 100)
        img.save(filename='/tmp/' + u[user_keys.user_role] + '.png')
        b = s3.bucket_straight(e[keys.entity_site])
        s3.save_s3(b, u[user_keys.user_role] + '/background.png', None, '/tmp/' + u[user_keys.user_role] + '.png', 'image/png')
    f.close()
    print u[user_keys.user_role], width, height 