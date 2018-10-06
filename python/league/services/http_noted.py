import requests
import pprint
import json
import sys

from pymongo import MongoClient

from league import keys_hollywood
from services import client
from app import fixed, communication_keys

from autobahn.twisted.websocket import WebSocketClientProtocol
from twisted.web import server, resource
from twisted.internet import threads
from amazon.dynamo import Tweet, Connection
from league.services.shared import SharedPath

media_type = 'media_type'

tv = 'tv'
movie = 'movie'

movie_results = 'movie_results'
tv_results = 'tv_results'
tmdb_id = 'id'

find_fmt = 'https://api.themoviedb.org/3/find/{}?api_key=80ac3b6d89c99d7278132e092f07e65b'
movie_fmt = 'https://api.themoviedb.org/3/movie/{}?api_key=80ac3b6d89c99d7278132e092f07e65b'
tv_fmt = 'https://api.themoviedb.org/3/tv/{}?api_key=80ac3b6d89c99d7278132e092f07e65b'

movie_collection = MongoClient().test.tmdb_movie
tv_collection = MongoClient().test.tmdb_tv
tmdb_collection = MongoClient().test.tmdb_find

def extract_imdb_id(url):
    return url.split('/')[-1]

def find_by_title(imdb_title):    
    find_dict = {keys_hollywood.imdb_title: imdb_title}    
    imdb_doc = tmdb_collection.find_one(find_dict)
    if imdb_doc:
        return fixed.to_json(imdb_doc)
    else:
        r = requests.get(find_fmt.format(imdb_title), params={'external_source': 'imdb_id'})
        if r.status_code == 200:
            imdb_json = r.json()
            imdb_json.update(find_dict)
            tmdb_collection.insert_one(imdb_json)
            return imdb_json

def get_tmdb_movie(movie_id):
    movie_dict = {tmdb_id: movie_id}
    cached_movie = movie_collection.find_one(movie_dict)
    if cached_movie:
        return fixed.to_json(cached_movie)
    else:
        movie_json = requests.get(movie_fmt.format(movie_id)).json()
        movie_json[media_type] = movie
        movie_collection.insert_one(movie_json)
        return fixed.to_json(movie_json)

def get_tmdb_tv(tv_id):
    
    tv_dict = {tmdb_id: tv_id}
    cached_tv = tv_collection.find_one(tv_dict)
    if cached_tv:
        return fixed.to_json(cached_tv)
    else:
        tv_json = requests.get(tv_fmt.format(tv_id)).json()
        tv_json[media_type] = tv
        tv_collection.insert_one(tv_json)
        return fixed.to_json(tv_json)         

def get_tmdb(imdb_title):
    imdb = find_by_title(imdb_title)
    #print 'imdb:', imdb
    if imdb[movie_results]:
        return get_tmdb_movie(imdb[movie_results][0][tmdb_id])
    elif imdb[tv_results]:
        return get_tmdb_tv(imdb[tv_results][0][tmdb_id])
    

class TmdbClientProtocol(WebSocketClientProtocol):
    
    def onOpen(self):
        print 'open add filter'
        webrole = {
            communication_keys.channel: communication_keys.listener,
            communication_keys.channel_filter: { keys_hollywood.noted: True, keys_hollywood.noted_profile: True }
        }
        self.sendMessage(json.dumps({Connection.webrole: webrole }))    
    
    def onMessage(self, payload, isBinary):
        if not isBinary:
            try:
                incoming = json.loads(payload)
                if keys_hollywood.noted_profile in incoming:
                    print 'incoming noted_profile:', incoming[keys_hollywood.noted_profile]
                    imdb_title = extract_imdb_id(incoming[keys_hollywood.noted_profile])
                    print 'imdb title:', imdb_title
                    tmdb_json = get_tmdb(imdb_title)                    
                    #pprint.pprint(tmdb_json)
                else:
                    print 'incoming:', incoming
            except Exception as e:
                print 'json failed:', e, payload, e.__class__.__name__

def error(err):
    print 'error:', err
    
class MovieResource(resource.Resource):

    isLeaf = True
    
    def response_headers(self, request):
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'GET')    
    
    def render_GET(self, request):
        SharedPath().response_headers(request, 'application/json')
        np = request.path[1:]
        print 'noted_ profile:', np
        d = threads.deferToThread(get_tmdb, np)
        d.addCallback(json.dumps)
        d.addCallback(request.write)
        d.addErrback(error)
        d.addBoth(lambda ign: request.finish())
        return server.NOT_DONE_YET    

movie_post = 8011

if __name__ == '__main__':
    endpoint = 'localhost'
    if len(sys.argv) > 1:
        endpoint = sys.argv[1] 
    from twisted.internet import reactor
    reactor.listenTCP(movie_post, server.Site(MovieResource()))    
    client.start_client(endpoint, TmdbClientProtocol)
    reactor.run()