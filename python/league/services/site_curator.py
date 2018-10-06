from twisted.web.resource import Resource

from league.services.match_resource import MatchResource, MissingResource
from league.services.profile_resource import ProfileResource
from league.services.entity_resource import EntityResource, OperatorResource, CuratorResource, LeagueResource, TeamResource
from league.services.conversation_resource import ConversationResource, MentionsResource, MentionedResource, QuoteResource
from league.services.auth_resource import AuthResource

from twisted.web import server
from twisted.internet import reactor

curator_port = 8011

if __name__ == '__main__':
    
    match = Resource()
    match.putChild('twitter', MatchResource())
    match.putChild('instagram', MatchResource())
    
    missing = Resource()     
    missing.putChild('twitter', MissingResource())
    missing.putChild('instagram', MissingResource())
    
    entity = EntityResource()
    entity.putChild('twitter', EntityResource())
    entity.putChild('instagram', EntityResource())
    
    recent = Resource()    
    recent.putChild('conversations', ConversationResource())
    recent.putChild('mentions', MentionsResource())
    recent.putChild('mentioned', MentionedResource())
    recent.putChild('quotes', QuoteResource())
    
    site = Resource()
    site.putChild('recent', recent)    
    site.putChild('operator', OperatorResource())
    site.putChild('curator', CuratorResource())
    site.putChild('league', LeagueResource())
    site.putChild('team', TeamResource())    
        
    root = Resource()    
    
    root.putChild('site', site)    
    root.putChild('entity', entity)    
    root.putChild('match', match)
    root.putChild('missing', missing)
    root.putChild('profile', ProfileResource())
    root.putChild('auth', AuthResource())
    
    reactor.listenTCP(curator_port, server.Site(root))    
    reactor.run()