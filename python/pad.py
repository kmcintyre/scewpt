import copy
from amazon.dynamo import Entity, User
from app import keys, user_keys
u = User().get_by_role('d1tweets.com', keys.entity_twitter)
for ln in  u[user_keys.user_site_leagues]:
    print ln
    for e in Entity().query_2(league__eq=ln):
        if e[keys.entity_profile].startswith('http://'):
            try:
                int(e[keys.entity_profile].split('/')[-1])
                print 'good profile:', e[keys.entity_profile]
            except:                                 
                ne = copy.deepcopy(e._data)
                new_profile = '/'.join(ne[keys.entity_profile].split('/')[:-1])
                ne[keys.entity_profile] = new_profile
                try:
                    ee = Entity().get_item(league=ln,profile=ne[keys.entity_profile] + 'blah')
                    print 'has'
                except:
                    ne_result = Entity().put_item(data=ne)
                    print 'create:', ne_result
                finally:
                    delete_result = e.delete()
                    print 'delete:', delete_result
                    
    
'''
from app import keys
import copy

for e in Entity().scan(index=Entity.index_team_profile, team__eq='Uab Uab'):
    e['team'] = 'UAB Blazers'
    e.partial_save()
'''
'''
import pystache
import os
from amazon.dynamo import User
from app import user_keys

with open('../build/xml/class.tmpl', 'r') as myfile:
    data=myfile.read()
    
for s in User().get_sites():
    site = s[user_keys.user_role].split('.')[0]
    for e in ['league', 'player', 'team']:
        m = { 'site': site, 'entity': e, 'csite': site.title(), 'centity': e.title() }
        c = pystache.render(data, m)
        try:
            os.makedirs('../polymer/site/')
        except:
            pass
        f = open('../polymer/site/' + s['role'].split('.')[0] + '-' + e + '.html', 'w')
        f.write(c)
        print site, e 
#print data
'''
'''
from amazon.dynamo import Entity
from app import keys
for t in Entity().scan(profile__beginswith='team:'):
    if not t[keys.entity_twitter]:
        print u'{:25s}'.format(t[keys.entity_league]), u'{:50s}'.format(t[keys.entity_profile].split(':')[1]) 


from amazon.dynamo import Tweet
from app import keys

for t in Tweet().query_2(index=Tweet.index_site, site__eq='athleets.com', limit=1, query_filter={'league__NOT_CONTAINS': ['nfl', 'tennis', 'bpl', 'laliga']}, reverse=True):
    print t['league']

from twisted.web.client import getPage
from twisted.internet import reactor, defer

def done(ans):
    print 'done!'

def test2():
    dl = defer.DeferredList(
        [
        getPage('http://service.athleets.com/profile/111104497'), 
        getPage('http://service.athleets.com/profile/170759111'),
        getPage('http://service.athleets.com/profile/727230138455363588'),
        getPage('http://service.athleets.com/profile/376037062')
        ]
    )
    dl.addCallback(done)
    return dl


def test():
    dl = defer.DeferredList([getPage('http://service.athleets.com/profile/111104497'), getPage('http://service.athleets.com/match/twitter')])
    dl.addCallback(done)
    return dl

reactor.callWhenRunning(test2)
reactor.run()  

from amazon.dynamo import Entity

for e in Entity().scan(profile__beginswith='team:'):
    if e['name'] or e['team']:
        print e['profile'], 'name:', e['name'], 'team:', e['team']
'''