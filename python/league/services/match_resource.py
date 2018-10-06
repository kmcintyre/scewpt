from amazon.dynamo import Entity, EntityHistory, User
from app import keys, time_keys, fixed
from twitter import twitter_keys

from twisted.web.resource import Resource

from twitter import tweets
from twisted.web import server

from twisted.internet import threads
from decimal import Decimal
import json
import time
from league.services import shared
from league import keys_league
from instagram import instagram_keys                          

class MissingResource(Resource):
    
    isLeaf = True
    
    def get_missing(self, args):
        return threads.deferToThread(Entity().query_2, **args)
    
    def render_GET(self, request):
        shared.SharedPath().response_headers(request, 'application/json')
        missing_key = request.prepath[-1] 
        hs = shared.hassocial(request, social_key = missing_key, is_null = True)
        print 'missing key:', missing_key, 'kwargs:', hs
        d = self.get_missing(hs)
        d.addCallback(lambda ans: shared.treat([e for e in ans]))
        d.addCallback(json.dumps, cls=fixed.SetEncoder)
        d.addCallback(request.write)
        d.addCallback(lambda ign: request.finish())
        return server.NOT_DONE_YET    

class MatchResource(Resource):
    
    isLeaf = True

    def find_by_profile(self, request, profile):
        if len(request.postpath) == 0 or request.postpath[0] == '':
            return [e for e in Entity().query_2(index=Entity.index_site_profile, site__eq=shared.SharedPath().path_site(request), profile__eq=profile)][0]
        elif len(request.postpath) == 1:
            return Entity().get_item(league=self.path_league(request)[keys.entity_league], profile=profile)
        elif len(request.postpath) == 2:
            return 
    
    def render_ERROR(self, code, message, request):
        request.setResponseCode(code)
        request.write(message)
        request.finish()    
        
    def render_POST(self, request):
        shared.SharedPath().response_headers(request, 'application/json')       
        body = json.loads(request.content.read())
        print 'match post:', request.prepath, 'uri:', request.uri, 'body:', body
        try:
            social_key = [sk for sk in keys_league.social_keys if sk in body][0]
            print 'social_key:', social_key
            if 'block' in body and body['block']:
                blocks = keys_league.add_blocked(shared.SharedPath().path_site(request), social_key, body[social_key])
                print 'blocks:', blocks                                                        
                if keys.entity_profile in body:
                    entity = self.find_by_profile(request, body[keys.entity_profile])
                    del entity[social_key]
                    del entity[getattr(keys, 'entity_match_' + social_key)]
                    entity.partial_save()
                request.write(json.dumps({'match' : 'blocked', keys.entity_profile : body[keys.entity_profile], social_key: body[social_key]}))
                request.finish()
                return server.NOT_DONE_YET
            elif 'no' in body and body['no']:
                entity = self.find_by_profile(request, body[keys.entity_profile])
                del entity[getattr(keys, 'entity_match_' + social_key)]
                entity.partial_save()
                request.write(json.dumps({'match' : 'deleted', keys.entity_profile : body[keys.entity_profile], social_key: body[social_key]}))
                request.finish()
                return server.NOT_DONE_YET                
            elif 'remove' in body and body['remove']:
                entity = self.find_by_profile(request, body[keys.entity_profile])
                if entity[social_key] == body[social_key]:
                    request.write('removed: ' + entity[social_key].encode('utf-8'))
                    del entity[social_key]
                    differences = { social_key + '__remove': entity[social_key], time_keys.ts_remove: int(time.time())}
                    EntityHistory().delta(entity, differences)
                    entity.partial_save()                    
                    request.finish()
                    return server.NOT_DONE_YET
                else:
                    self.render_ERROR(400, 'Cannot Remove:' + str(body[social_key]), request)
                    return server.NOT_DONE_YET        
            else:
                entity = self.find_by_profile(request, body[keys.entity_profile]) 
                body[social_key] = body[social_key][1:] if body[social_key][:1] == '@' else body[social_key]
                if not entity[social_key] or 'overwrite' in body and body['overwrite']:
                    entity[social_key] = body[social_key]
                    if (social_key == keys.entity_twitter and twitter_keys.validate_twitter(entity)) or (social_key == keys.entity_instagram and instagram_keys.validate_instagram(entity)):
                        return self.identify(social_key, entity, request)
                    else:
                        print 'league has:', social_key, 'value:', entity[social_key]
                        self.render_ERROR(400, 'Invalid:' + entity[social_key].encode('utf-8'), request)
                        return server.NOT_DONE_YET
                else:
                    print 'already has:', social_key, 'value:', entity[social_key]
                    self.render_ERROR(409, 'Already Has:' + entity[social_key].encode('utf-8'), request)
                    return server.NOT_DONE_YET
        except Exception as e:
            print 'social key exception:', e               

    def identify(self, social_key, entity, request):
        differences = { social_key + '__add': entity[social_key], 'ts_match_' + social_key: int(time.time())}
        print 'valid:', social_key, entity[social_key]
        if entity['match_' + social_key]:
            del entity['match_' + social_key]                            
        entity.partial_save()
        EntityHistory().delta(entity, differences)
        league = Entity().get_item(league=entity[keys.entity_league], profile=Entity().league_profile(entity[keys.entity_league]))
        curator = User().get_curator(entity[keys.entity_league])
        tweet_txt = getattr(tweets, 'id_' + social_key)(entity, curator, league) 
        try:
            print 'tweet message:', tweet_txt
        except:
            pass
        tweet_message = {}
        tweet_message.update(entity._data)                            
        tweet_message[twitter_keys.message_tweet] = tweet_txt
        request.write(json.dumps(tweet_message, cls=fixed.SetEncoder))
        request.finish()
        return server.NOT_DONE_YET

    def get_match(self, args):
        return threads.deferToThread(Entity().query_2, **args)

    def render_GET(self, request):  
        shared.SharedPath().response_headers(request, 'application/json')
        match_key = 'match_' + request.prepath[-1]
        hs = shared.hassocial(request, match_key)
        print 'match key:', match_key, 'kwargs:', hs
        self.get_match(hs).addCallback(
            lambda ans: shared.treat([e for e in ans if not isinstance(e[match_key], Decimal)])
        ).addCallback(json.dumps, cls=fixed.SetEncoder).addCallback(request.write).addCallback(lambda ign: request.finish())
        return server.NOT_DONE_YET                       