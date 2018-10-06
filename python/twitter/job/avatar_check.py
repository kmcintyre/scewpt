from amazon.dynamo import Entity, ProfileTwitter
from amazon import s3
from app import keys
import requests
from boto.s3.key import Key
from app import fixed, misc
import urllib2
import subprocess
from twitter.job import scout

size = 'large'

for entity in Entity().scan(twitter__null=False):    
    try:
        size_avatar = 'http://' + entity[keys.entity_site] + '/tw/' + entity[keys.entity_twitter_id] + '/avatar_' + size + '.png'
        r = requests.head(size_avatar)
        if r.status_code == 403:
            print 'https://twitter.com/' + entity[keys.entity_twitter]
            media = s3.get_twitter_media(entity, size)
            if media:
                print entity._data
                print 
                key = Key(s3.bucket_straight(entity[keys.entity_site]))
                key.name = 'tw/' + entity[keys.entity_twitter_id] + '/avatar_' + size + '.png'
                key.set_redirect('http://s3.amazonaws.com/' + media[0].bucket.name + '/' + media[0].name)
                key.make_public()
                print 'http://' + key.bucket.name + '/' + key.name
                #exit(-1)                     
            else:
                current = ProfileTwitter().profile_last(entity[keys.entity_twitter_id])
                if current:
                    avi_compare_url = '_400x400'.join(current[ProfileTwitter.profile_image_url].rsplit('_normal', 1))
                    avi_url = fixed.clean_url(avi_compare_url)
                    local_large_avi_path = '/tmp/large/' + entity[keys.entity_twitter] + avi_url[avi_url.rindex('.'):]
                    fixed.filesubpath(local_large_avi_path)
                    resize_local_large_avi_path = '/tmp/resize/large/' + entity[keys.entity_twitter] + '.png'
                    fixed.filesubpath(resize_local_large_avi_path)            
                    try:
                        with open(local_large_avi_path, 'w') as large_file:
                            response = urllib2.urlopen(avi_compare_url).read()
                            large_file.write(response)
                            #print 'done writing to file', local_large_avi_path
                        if local_large_avi_path[-3:].lower() == 'jpg' or local_large_avi_path[-4:].lower() == 'jpeg':
                            new_local_large_avi_path = '/tmp/large/png/' + entity[keys.entity_twitter] + '.png'
                            fixed.filesubpath(new_local_large_avi_path)
                            args = ['convert', local_large_avi_path, new_local_large_avi_path]
                            subprocess.check_call(args)
                            local_large_avi_path = new_local_large_avi_path                                    
                        
                        
                        avi_meta = {}
                        avi_meta.update(current)
                        avi_meta.update(entity._data)
                        
                        s3.save_avi('orig', avi_compare_url, local_large_avi_path, avi_meta)            
                        #print 'large avatar local:', local_large_avi_path
                        resize_args = ['convert', local_large_avi_path, '-resize', '210x210^', resize_local_large_avi_path]
                        subprocess.check_call(resize_args)                
                        misc.round_corners(resize_local_large_avi_path, 'large')                            
                        s3.save_avi('large', avi_compare_url, resize_local_large_avi_path, avi_meta)
                        scout.small_sync(entity, current)                                
                    except:
                        print 'missing avatar image!'
                else:
                    print 'missing current'
    except Exception as e:
        print 'avatar check exception:', e, entity._data