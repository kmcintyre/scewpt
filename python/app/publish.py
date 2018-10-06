import os
import sys
from glob import glob

from amazon import s3
from amazon.dynamo import User
from app import user_keys

publish_filters = ['*.html', 'bower_components/webcomponentsjs/webcomponents-*.js', 'bower_components/webcomponentsjs/webcomponents-*.js.map', 'bower_components/webcomponentsjs/custom-elements-es5-adapter.js']

regular_files = []

def get_build_dir(site):
    return '/home/ubuntu/' + site + '/build/es5-bundled'

def get_publish_list(site):    
    pl = set([])
    for pf in publish_filters:
        result = [y for x in os.walk(get_build_dir(site)) for y in glob(os.path.join(x[0], pf))]
        for res in result:
            pl.add(res)
    return list(pl)

def do_publish(site):
    b = s3.bucket_straight(site)         
    for res in get_publish_list(site):    
        publish_to = res[len(get_build_dir(site))+1:]
        key = s3.save_s3(b, publish_to, None, res, None, 'public-read', None, 'gzip')
        print publish_to, 'to:', key.name
    key = s3.save_s3(b, 'intersection-observer.js', None, '/home/ubuntu/' + site + '/intersection-observer.js', None, 'public-read', None, 'gzip')
    
        
if __name__ == '__main__':
    try:
        do_publish(sys.argv[1])
    except:
        for u in User().get_curators():
            do_publish(u[user_keys.user_role])
        
