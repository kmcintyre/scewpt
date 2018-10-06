import boto3
s3 = boto3.resource('s3')
s3_client=boto3.client('s3')

from amazon.dynamo import Entity, User
from app import keys, user_keys
from twisted.internet import threads, reactor
import sys
import os

leagues = []
if len(sys.argv) > 1:
    leagues.append(sys.argv[1])

def publish_loop():
    for site in User().get_sites():
        b = s3.Bucket(site[user_keys.user_role])
        for league_name in [l for l in site[user_keys.user_site_leagues] if not leagues or l in leagues]:
            league = Entity().get_league(league_name)
            prefix_1 = (league[keys.entity_league] if league[keys.entity_emblem] is None else league[keys.entity_emblem]) + '/logo/'
            prefix_2 = (league[keys.entity_league] if league[keys.entity_emblem] is None else league[keys.entity_emblem]) + '/logo_standard/'
            for prefix in [prefix_1,prefix_2]:
                for logo in os.listdir('/home/ubuntu/' + site[user_keys.user_role] + '/' + prefix):
                    fp = '/home/ubuntu/' + site[user_keys.user_role] + '/' + prefix + logo
                    objs = list(b.objects.filter(Prefix=prefix + logo))
                    print b.name, logo
                    if len(objs) > 0 and len(sys.argv) < 2:
                        print 'exists:', logo
                    else:
                        print 'missing or overwrite:', logo
                        data = open(fp, 'rb')        
                        b.put_object(ACL='public-read', Key=prefix + logo, Body=data, ContentType='image/svg+xml')                    
def done_publish(ign=None):
    print 'done_publish:', ign
    reactor.stop()

def publish_start():
    d = threads.deferToThread(publish_loop)
    d.addBoth(done_publish)

if __name__ == '__main__':
    reactor.callWhenRunning(publish_start)
    reactor.run()