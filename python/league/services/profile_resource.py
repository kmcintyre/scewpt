import json

from amazon.dynamo import ProfileTwitter

from twisted.internet import defer, threads
from twisted.web import server, resource
from twisted.web.resource import NoResource
from app import fixed, keys

from pymongo import MongoClient
from league.services.shared import SharedPath

profile_created = 'profile_created'

profile_collection = MongoClient().test.profile_collection
profile_collection.create_index(profile_created, expireAfterSeconds = 3600 * 24 )

def add_profile(tp):
    profile_collection.insert_one(json.loads(json.dumps(tp._data, cls=fixed.SetEncoder)))
    return tp._data

def error_profile(err, request):
    print 'error profile:', err
    request.write('')

def get_profile(twitter_id, ts):
    profile_dict = {keys.entity_twitter_id: twitter_id}
    print json.dumps(profile_dict)
    cached_profile = profile_collection.find_one(profile_dict)
    if cached_profile:
        return defer.succeed(fixed.to_json(cached_profile))
    elif ts:
        kwargs = {
            'twitter_id': twitter_id,
            'ts_add': ts
        }
        return threads.deferToThread(ProfileTwitter().get_item, **kwargs).addCallback(add_profile).addErrback(lambda ign: get_profile(twitter_id, None))
    else:
        kwargs = ProfileTwitter().profile_args_since(twitter_id)            
        return threads.deferToThread(ProfileTwitter().query_2, **kwargs).addCallback(
            lambda ans: [a for a in ans]
        ).addCallback(
            lambda ans: add_profile(ans[0])
        )                 

def error(err, request):
    print 'error:', err, request
    return NoResource()

class ProfileResource(resource.Resource):

    isLeaf = True
    
    def render_GET(self, request):
        SharedPath().response_headers(request, 'application/json')        
        twitter_id = request.postpath[0]
        ts = None
        if len(request.postpath) > 1: 
            ts = int(request.postpath[1])
        print 'profile:', twitter_id, 'ts:', ts
        get_profile(twitter_id, ts).addCallback(json.dumps, cls=fixed.SetEncoder).addCallback(request.write).addErrback(error_profile, request).addBoth(lambda ign: request.finish())         
        return server.NOT_DONE_YET          