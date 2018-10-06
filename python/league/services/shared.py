from app import keys, communication_keys, user_keys, fixed

from amazon.dynamo import Entity, User

def treat(resp):
    from boto.dynamodb2.items import Item
    if isinstance(resp, dict):
        return resp 
    elif isinstance(resp, Item):
        return resp._data
    elif isinstance(resp, list):
        return [treat(i) for i in resp]
    else:
        return resp

def dump(resp):
    import json
    return json.dumps(treat(resp), cls=fixed.SetEncoder)

def entity_filter(entity):
    return dict((key,value) for key, value in entity.items() if key not in [user_keys.user_twitter_auth, user_keys.user_type, user_keys.user_auth_token_secret, user_keys.user_auth_token, user_keys.user_password, user_keys.user_username, user_keys.user_twitter_apps, user_keys.user_twitter_auth])        

def hassocial(request, social_key = None, is_null = False):
    missing_args = {}
    if social_key:        
        missing_args['query_filter'] = { social_key + '__null': is_null }        
    if len(request.postpath) == 0 or request.postpath[0] == '':
        missing_args['index'] = Entity.index_site_profile
        missing_args['site__eq'] = SharedPath().path_site(request)
    elif len(request.postpath) == 1:
        print 'league parent'
        missing_args['league__eq'] =  request.postpath[0]
    elif len(request.postpath) == 2:
        print 'team parent'
        missing_args['index'] = Entity.index_team_profile            
        missing_args['team__eq'] = request.postpath[1]                                
    return missing_args

class SharedPath():
    
    def response_headers(self, request, content_type = None):
        if content_type:
            request.setHeader('Content-Type', content_type)       
    
    def error_render(self, e, request):
        print 'error render:', e
        request.setResponseCode(503)

    def path_site(self, request):
        return communication_keys.host(request.getRequestHostname())

    def path_curator(self, request):
        return User().get_by_role(self.path_site(request), keys.entity_twitter)

    def path_league(self, request):
        return Entity().get_item(league=request.prepath[1], profile='league:' + request.prepath[1])

    def path_team(self, request):
        tn = 'team:' + request.prepath[2]
        return Entity().get_item(league=request.prepath[1], profile=tn)

    def path_property_entity(self, request):
        return Entity().get_item(league=self.path_league(request)[keys.entity_league], profile=request.postpath[0])
