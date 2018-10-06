from twisted.web import resource, server
from twisted.web.resource import NoResource
 
from league.services import shared
from amazon.dynamo import Entity, User

from twisted.internet import threads

from app import keys, fixed

import json

def error(err, request):
    print 'error:', err, request
    return NoResource()

def entity_error(err):
    print 'entity error:', err

def deferred_user(request, kwargs):
    threads.deferToThread(User().query_2, **kwargs).addCallback(
        lambda ans: [a for a in ans]
    ).addCallback(
        lambda ans: json.dumps(shared.treat(shared.entity_filter(ans[0]._data)),cls=fixed.SetEncoder)
    ).addCallback(request.write).addCallback(
        lambda ign: request.finish()
    ).addErrback(error, request)

class OperatorResource(resource.Resource):
    
    isLeaf = True
    
    def render_GET(self, request):
        shared.SharedPath().response_headers(request, 'application/json')
        if len(request.postpath) > 0:
            kwargs = User().get_role_args(request.postpath[0], keys.entity_twitter)
            print 'get operator:', kwargs
            deferred_user(request, kwargs)
        else:
            site = shared.SharedPath().path_site(request)
            threads.deferToThread(User().get_leagues, site, keys.entity_twitter).addCallback(
                lambda ans: json.dumps([shared.treat(shared.entity_filter(u._data)) for u in ans],cls=fixed.SetEncoder) 
            ).addCallback(request.write).addCallback(
                lambda ign: request.finish()
            )            
        return server.NOT_DONE_YET

class CuratorResource(resource.Resource):
    
    isLeaf = True
    
    def render_GET(self, request):
        shared.SharedPath().response_headers(request, 'application/json')
        kwargs = User().get_role_args(shared.SharedPath().path_site(request), keys.entity_twitter)
        print 'get curator:', kwargs
        deferred_user(request, kwargs)
        return server.NOT_DONE_YET   

class TeamResource(resource.Resource):
    
    isLeaf = True
    
    def render_GET(self, request):
        shared.SharedPath().response_headers(request, 'application/json')
        kwargs = {
            'league': request.postpath[0], 
            'profile':'team:' + request.postpath[1]
        }
        print 'get team:', kwargs
        threads.deferToThread(Entity().get_item, **kwargs).addCallback(
            lambda ans: json.dumps(shared.treat(ans),cls=fixed.SetEncoder)
        ).addCallback(request.write).addCallback(
            lambda ign: request.finish()
        )    
        return server.NOT_DONE_YET 
    
class LeagueResource(resource.Resource):
    
    isLeaf = True
    
    def render_GET(self, request):
        shared.SharedPath().response_headers(request, 'application/json')
        kwargs = {
            'league': request.postpath[0], 
            'profile' : Entity().league_profile(request.postpath[0])
        }
        print 'get league:', kwargs 
        threads.deferToThread(Entity().get_item, **kwargs).addCallback(
            lambda ans: json.dumps(shared.treat(ans),cls=fixed.SetEncoder)
        ).addCallback(request.write).addCallback(
            lambda ign: request.finish()
        )
        return server.NOT_DONE_YET       
        
class EntityResource(resource.Resource):

    isLeaf = True
    
    def render_GET(self, request):
        shared.SharedPath().response_headers(request, 'application/json')
        kwargs = shared.hassocial(request, social_key = request.prepath[1] if len(request.prepath) > 1 else None, is_null = False)
        print 'get entity:', kwargs
        #threads.deferToThread(Entity().query_2, **kwargs).addCallback(
        #    lambda ans: json.dumps([shared.treat(e) for e in ans],cls=fixed.SetEncoder)
        #).addCallback(request.write).addCallback(
        #    lambda ign: request.finish()
        #).addErrback(entity_error)            
        return server.NOT_DONE_YET