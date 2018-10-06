from twisted.web import resource, server
from twisted.web.resource import NoResource
 
from league.services import shared
from amazon.dynamo import Tweet

from pymongo import MongoClient

from app import fixed
import json

def error(err, request):
    print 'error:', err, request
    return NoResource()

class MongoResource(resource.Resource):
    
    find_limit = 20
    isLeaf = True
    mongo_db = MongoClient().test
    
    def render_GET(self, request):
        shared.SharedPath().response_headers(request, 'application/json')
        l = request.postpath 
        site = shared.SharedPath().path_site(request)
        print 'get:', l, request.prepath, request.args
        cs = '_'.join([self.prefix, site.split('.')[0]])
        resp = fixed.to_json([c for c in self.mongo_db[cs].find({}).sort(Tweet.ts_ms, -1).skip(0 if 'skip' not in request.args else int(request.args['skip'][0])).limit(self.find_limit)])
        print 'collection name:', cs, 'response length:', len(resp)
        request.write(json.dumps(resp, cls=fixed.SetEncoder))         
        request.finish()
        return server.NOT_DONE_YET    


class ConversationResource(MongoResource):
    
    prefix = 'conversation'
    
class MentionsResource(MongoResource):
    
    prefix = 'mentions'
    
class QuoteResource(MongoResource):
    
    prefix = 'quote'
    
class MentionedResource(MongoResource):
    
    prefix = 'mentioned'
    