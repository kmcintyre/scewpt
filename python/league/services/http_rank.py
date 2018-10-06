import pprint
import json
import time
import sys
from pymongo import MongoClient

from app import keys, fixed, time_keys, communication_keys
from league import keys_league
from services import client
from amazon.dynamo import EntityHistory , Connection

from league.services.shared import SharedPath

from autobahn.twisted.websocket import WebSocketClientProtocol

from twisted.web import server, resource
from twisted.internet import threads

ranking_created = 'ranking_created'
ranking_list = 'ranking_list'

ranking_collection = MongoClient().test.ranking
ranking_collection.create_index( ranking_created, expireAfterSeconds = 3600 * 24 )

ranking_query = {
    'query_filter': {'rank__add__null': False, 'rank__change__null': False, 'rank__remove__null': False},
    'conditional_operator': 'OR',
    'attributes': ('rank__add', 'rank__change', 'rank__remove', 'ts_add'),
    'reverse': True
}

def create_rankings(league_name, league_profile):
    return [e._data for e in EntityHistory().query_2(profile__eq=league_profile, **ranking_query)]


def get_rankings(league_name, league_profile):
    print 'league', league_name, 'profile:', league_profile
    ranking_dict = {keys.entity_league: league_name, keys.entity_profile: league_profile}
    cached_ranking = ranking_collection.find_one(ranking_dict)
    if cached_ranking:
        return fixed.to_json(cached_ranking)
    else:
        ranks = create_rankings(league_name, league_profile)
        rankings = []
        rank = None
        for r in ranks:
            if 'rank__change' in r:
                rank = r['rank__change'].split('__')[1]
            elif 'rank__add' in r:                            
                rank = r['rank__add']
            elif 'rank__remove' in r:
                rank = None                
            rankings.append({ keys_league.rank: rank, time_keys.ts: int(r[time_keys.ts_add])})                                                    
        ranking_dict[ranking_list] = rankings
        ranking_dict[ranking_created] = int(time.time())
        ranking_collection.insert_one(ranking_dict)
        return fixed.to_json(ranking_dict)    

class RankingClientProtocol(WebSocketClientProtocol):
    
    def onOpen(self):
        print 'open add filter'        
        webrole = {            
            communication_keys.channel: communication_keys.listener,
            communication_keys.channel_filter: {keys_league.rank: True }
        }
        self.sendMessage(json.dumps({Connection.webrole: webrole }))    
    
    
    def onMessage(self, payload, isBinary):
        if not isBinary:
            try:
                incoming = json.loads(payload)
                if keys.entity_league in incoming and keys.entity_profile in incoming:
                    print 'rankings:', get_rankings(incoming[keys.entity_league], incoming[keys.entity_profile])
                else:
                    #print 'incoming:', incoming
                    pass
            except Exception as e:
                print 'json failed:', e, payload, e.__class__.__name__

def error(err):
    print 'error:', err
    
class RankingResource(resource.Resource):

    isLeaf = True
    
    def render_POST(self, request):
        SharedPath().response_headers(request, 'application/json')
        body = json.loads(request.content.read())
        print 'body:', body
        league_name = body[keys.entity_league]
        print league_name
        league_profile = body[keys.entity_profile]
        print league_profile
        d = threads.deferToThread(get_rankings, league_name, league_profile)
        d.addCallback(json.dumps)
        d.addCallback(request.write)
        d.addErrback(error)
        d.addBoth(lambda ign: request.finish())
        return server.NOT_DONE_YET    

ranking_post = 8012

if __name__ == '__main__':    
    endpoint = 'localhost'
    if len(sys.argv) > 1:
        endpoint = sys.argv[1] 

    from twisted.internet import reactor
    reactor.listenTCP(ranking_post, server.Site(RankingResource()))    
    client.start_client(endpoint, RankingClientProtocol)
    reactor.run()