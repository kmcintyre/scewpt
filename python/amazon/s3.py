import boto
from boto.s3.key import Key

import mimetypes

from app import fixed, keys
import json
import StringIO
import gzip

def curator_md5(bucket, filename):
    try:
        md5 = check_key(bucket, filename).metadata['md5']
        print 'md5:', md5
        return md5 
    except Exception as e:
        print e

def check_key(bucket, filename):
    try:
        possible_key = bucket.get_key(key_name=filename)
        key = bucket.lookup(possible_key.name)
        if key is not None:
            return key
        else:
            print 'is none key', bucket, filename
            return False
    except:
        print 'key missing:', 'http://s3.amazonaws.com/' + bucket.name + '/' + filename
        return False

def bucket_straight(bucket_name):
    try:
        conn = boto.connect_s3()
        b = conn.get_bucket(bucket_name)
        return b
    except Exception as e:
        
        print 'missing bucket?:', bucket_name, e.__class__.__name__, e.__module__
        raise e


def subdomain_bucket(subdomain, site):
    if site and subdomain:
        full_domain = subdomain + '.' + site
        try:
            return bucket_straight(full_domain)
        except Exception as e:
            print 'creating a bucket:', full_domain, e
            return boto.connect_s3().create_bucket(full_domain)
    else:
        last_ditch = subdomain + '.scewpt.com'
        print 'null site for subdomain - last ditch?:', last_ditch

def get_redirect(bucket, path):
    possible_key = bucket.get_key(key_name=path)
    return possible_key.get_redirect()
    
def create_local_redirect(bucket, path, location):
    print 'attempt local_redirect', bucket.name, path, location
    key = Key(bucket)
    key.name = path
    key.set_contents_from_string('')
    key.set_redirect(location)
    key.make_public()
    print 'local_redirect', bucket.name, path, location

def save_s3(bucket, filename, contents, systemfile, content_type=None, acl='public-read', meta=None, encode=None):
    from boto.dynamodb2.table import Item
    key = Key(bucket, filename)
    print 'new s3 key:', 'http://s3.amazonaws.com/' + bucket.name + (key.name if key.name.startswith('/') else '/' + key.name)
    if isinstance(meta, Item):
        meta = meta._data
    if isinstance(meta, dict):
        trim_meta = fixed.check_entity_size(meta)
        trim_meta = dict([(k, value) for (k, value) in trim_meta.items() if value is not None and value])
        trim_meta = json.loads(json.dumps(trim_meta, cls=fixed.SetEncoder))
        print 'meta key length:', len(trim_meta.keys()) 
        key.metadata = trim_meta
    if content_type is not None:
        print 'set content type:', content_type
        key.content_type = content_type
    elif systemfile and systemfile.endswith('js.map'):
        print 'js map!'
        key.content_type = 'application/json'                                                              
    elif systemfile:        
        gt = mimetypes.guess_type(systemfile)
        key.set_metadata('Content-Type', gt[0])    
    if encode is not None and encode == 'gzip':
        key.set_metadata('Content-Encoding', 'gzip')    
        gzmem = StringIO.StringIO()
        gzip_file = gzip.GzipFile(fileobj = gzmem, mode = 'w')
        if contents is not None:
            gzip_file.write(contents)
        elif systemfile is not None:
            with open(systemfile, 'rb') as outfile:
                gzip_file.write(outfile.read())
        gzip_file.close()
        key.set_contents_from_string(gzmem.getvalue())
        print 'gzip!'
    elif contents is not None:
        print 'from string'
        key.set_contents_from_string(contents)
    elif systemfile is not None:        
        io = StringIO.StringIO(open(systemfile, 'r').read()).getvalue()
        print 'from disk:', systemfile, 'io:', len(io)
        key.set_contents_from_string(io)
    if acl is not None:
        print 'save acl:', acl
        key.set_acl(acl)                
    print 'save complete:', key.name            
    return key

def get_twitter_media(entity, size='small'):
    media = []
    pf = 'tw/' + entity[keys.entity_twitter_id] + '/' + size + '/'
    for avi in bucket_straight('socialcss.com').get_all_keys(prefix=pf):
        if avi.name.endswith('/'):
            pass
        elif avi.size == 0:
            subavi = avi            
            while subavi.get_redirect():
                url = subavi.get_redirect().split('//')[1]
                avi_domain = url.split('/', 2)[1]
                avi_path = url.split('/', 2)[2]                
                subavi = bucket_straight(avi_domain).get_key(avi_path)                
            #print 'redirect:', 'http://s3.amazonaws.com/' + subavi.bucket.name + '/' + subavi.name
            media.append(subavi)
        else:
            #print 'link:', 'http://socialcss.com.s3-website-us-east-1.amazonaws.com/' + avi.name
            #print size + ':', avi.name, avi.last_modified
            media.append(avi)
    media.sort(key=lambda k: fixed.key_dt(k), reverse=True)    
    #print [s.last_modified for s in media]    
    return media

def save_bg(background_url, systemfile, meta):
    print 'save_bg:', meta[keys.entity_league], 'twitter id:', meta[keys.entity_twitter_id], 'url:', background_url
    s3_filename = 'tw/' + meta[keys.entity_twitter_id] + '/background/' + fixed.digest(background_url) + '.png'
    save_bg_key = save_s3(
        bucket_straight('socialcss.com'),
        s3_filename,
        None,
        systemfile,
        'image/png',
        'public-read',
        meta
    )
    print 'save_background saved!', 'http://s3.amazonaws.com/socialcss.com/' + save_bg_key.name
    redirect_url = 'http://socialcss.com.s3-website-us-east-1.amazonaws.com/' + s3_filename         
    try:
        key = Key(bucket_straight(meta[keys.entity_site]))
        key.name = 'tw/' + meta[keys.entity_twitter_id] + '/background.png'
        key.set_redirect(redirect_url)
        key.make_public()
    except Exception as e:
        print 'pub background exception:', e        

def save_insta_avi(avatar_url, systemfile, meta):
    print 'save inst avi:', meta[keys.entity_league], 'instagram id:', meta[keys.entity_instagram_id],'url:', avatar_url
    s3_filename = 'insta/' + meta[keys.entity_instagram_id] + '/' + fixed.digest(avatar_url) + '.png'
    save_s3(
        bucket_straight('socialcss.com'),
        s3_filename,
        None,
        systemfile,
        'image/png',
        'public-read',
        meta
    )        
    redirect_url = 'http://socialcss.com.s3-website-us-east-1.amazonaws.com/' + s3_filename
    try:
        key = Key(bucket_straight(meta[keys.entity_site]))
        key.name = 'insta/' + meta[keys.entity_instagram_id] + '/avatar.png'
        key.set_redirect(redirect_url)
        key.make_public()
        print 'insta redirect:', 'http://' + meta[keys.entity_site] + '/' + key.name
    except Exception as e:
        print 'pub avi exception:', e
            
def save_avi(size, avatar_url, systemfile, meta):
    print 'save_avi:', meta[keys.entity_league], 'size:', size, 'twitter id:', meta[keys.entity_twitter_id],'url:', avatar_url
    s3_filename = 'tw/' + meta[keys.entity_twitter_id] + '/' + size + '/' + fixed.digest(avatar_url) + '.png'
    save_avi_key = save_s3(
        bucket_straight('socialcss.com'),
        s3_filename,
        None,
        systemfile,
        'image/png',
        'public-read',
        meta
    )
    print 'save_avi saved!', 'http://s3.amazonaws.com/socialcss.com/' + save_avi_key.name
    redirect_url = 'http://socialcss.com.s3-website-us-east-1.amazonaws.com/' + s3_filename         
    try:
        key = Key(bucket_straight(meta[keys.entity_site]))
        key.name = 'tw/' + meta[keys.entity_twitter_id] + '/avatar_' + size + '.png'
        key.set_redirect(redirect_url)
        key.make_public()
    except Exception as e:
        print 'pub avi exception:', e