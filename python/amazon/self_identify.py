from twisted.internet import reactor, defer, task

import boto.ec2
import boto.route53

import os
import time

from app import keys, user_keys
from amazon.dynamo import User
from amazon import identify_service

startup_init = """
[Unit]
Description={0} Service

[Service]
User=ubuntu
EnvironmentFile=/home/ubuntu/scewpt/etc/python.env
WorkingDirectory=/home/ubuntu/scewpt/python
ExecStart=/usr/bin/python /home/ubuntu/scewpt/python/twitter/user_stream.py {0} {1}
Restart=always
ExecStartPre=/bin/sleep 10

[Install]
WantedBy=multi-user.target
"""
                
def operate_site(league, curator):
    print 'operator site:', league    
    fn = 'twitter_' + league + '.service'
    if not os.path.isfile('/etc/systemd/system/' + fn):
        with open('/tmp/' + fn, 'wt') as init_file:
            init_file.write(startup_init.format(league, 'service.' + curator).strip())
        os.system('sudo chown root:root /tmp/' + fn)
        os.system('sudo mv /tmp/' + fn + ' /etc/systemd/system/' + fn)
        enable_start('twitter_' + league)
    else:
        print 'already in operate site:', league

def enable_start(service_name):
    print 'enable and start:', service_name
    os.system('sudo systemctl enable ' + service_name + '.service')
    os.system('sudo systemctl start ' + service_name )
    
def disable_start(service_name):
    print 'disable and stop:', service_name
    os.system('sudo systemctl disable ' + service_name + '.service')
    os.system('sudo systemctl stop ' + service_name )
        
def cname_helper(hz, instance, cname, tagname):
    cname_tagname = cname + '.' + tagname           
    print 'cname:', cname_tagname     
    if hz.find_records(cname_tagname, 'CNAME'):
        #print 'update league cname:', cname_tagname
        hz.update_cname(
            cname_tagname, instance.public_dns_name, ttl=300, identifier=None, comment='Webserver for:' + hz.name
            )
    else:
        #print 'add league cname:', cname_tagname
        hz.add_cname(
            cname_tagname, instance.public_dns_name, ttl=300, identifier=None, comment='Webserver for:' + hz.name)
    

def operate_tag(tagname, instance):
    print 'identify_service tagname:', tagname    
    if tagname in ['service']:
        enable_start('mongod')
        operate_service('services_websocket')
        operate_service('site_curator')
        operate_service('services_mongo_cache')
        for hz in boto.route53.connection.Route53Connection().get_zones():            
            fullname = tagname + '.' + hz.name
            print 'hz!:', hz.name, 'ip address:', instance.ip_address, 'public dns:', instance.public_dns_name
            if hz.name[:-1] in [u[user_keys.user_role] for u in User().get_sites()] or hz.name[:-1] == 'socialcss.com': 
                cname_helper(hz, instance, tagname, hz.name)                
            elif hz.find_records(fullname, 'CNAME'):
                print 'remove cname'
                hz.delete_cname(fullname)                                    
    elif tagname == 'mail':
        operate_service('services_xmlrpc')
        operate_service('services_mail')
        operate_service('tweet_router')
        operate_service('tweet_queue_check')        
        for hz in boto.route53.connection.Route53Connection().get_zones():
            try:
                mx = hz.get_mx(hz.name)
                current_mx = mx.resource_records[0].split(' ')[1]
                if instance.public_dns_name != current_mx[:-1]:
                    hz.update_mx(hz.name, "20 " + instance.public_dns_name,
                                 ttl=300, identifier=None, comment='Mail for:' + hz.name)
                    print 'update_mx for hz:', instance.public_dns_name, hz.name
                else:
                    pass
                    #print 'hz!:', hz.name, 'mx is good:', current_mx[:-1]
                if hz.name == 'scewpt.com.':
                    print 'mail:' + current_mx[:-1]
                    tagname = 'mail.scewpt.com.'
                    if hz.find_records(tagname, 'CNAME'):
                        #print 'hz!:', hz.name, 'update mail.scewpt.com cname'
                        hz.update_cname(
                            tagname, instance.public_dns_name, ttl=300, identifier=None, comment='MailServer for:' + hz.name)
                    else:
                        #print 'hz!:', hz.name, 'add mail.scewpt.com cname'
                        hz.add_cname(tagname, instance.public_dns_name, ttl=300, identifier=None, comment='MailServer for:' + hz.name)
            except Exception as e:
                print 'create mail for hz:', hz, e
                hz.add_mx(hz.name, "20 " + instance.public_dns_name, ttl=300,
                          identifier=None, comment='MailServer for:' + hz.name)
    elif tagname in ['bible', 'cleansocial', 'instagram', 'match', 'following', 'scout-alt', 'scout', 'stalk', 'stalk-alt']:
        zone_tag = tagname + '.scewpt.com'
        hz = boto.route53.connection.Route53Connection().get_zone('scewpt.com.')
        if hz.find_records(zone_tag, 'CNAME'):
            hz.update_cname(zone_tag, instance.public_dns_name, ttl=300, identifier=None, comment='Webserver for:' + hz.name)
        else:
            hz.add_cname(zone_tag, instance.public_dns_name, ttl=300, identifier=None, comment='Webserver for:' + hz.name)
        print 'tagname:', tagname                
        operate_service(tagname)
        operate_service('services_xmlrpc')                
    elif '.' in tagname:
        operate_service('site_activity')
        operate_service('services_xmlrpc')
        print 'domain:', tagname
        hz = boto.route53.connection.Route53Connection().get_zone(tagname)        
                            
        curator = User().get_by_role(tagname, keys.entity_twitter)        
        print 'zone:', hz.name[:-1], 'ip address:', instance.ip_address, 'public dns:', instance.public_dns_name
        for cname in ['dev']:
            cname_helper(hz, instance, cname, tagname)
        for league in curator[user_keys.user_site_leagues]:
            if league == 'hollywood':
                operate_service('services_avatar')
                operate_service('services_background')
            elif league == 'aac':
                operate_service('services_scout')
            elif league == 'bpl':
                operate_service('services_inflate')
                                
            league_user = User().get_by_role(league, keys.entity_twitter)
            if league_user[user_keys.user_twitter_apps] and len(league_user[user_keys.user_twitter_apps].keys()) > 0 and not league_user[user_keys.user_locked]:
                cname_helper(hz, instance, league_user[user_keys.user_role] , tagname)
                operate_site(league, curator[user_keys.user_role])
            else:
                print 'skipping:', league
        return curator            
        
def operate_service(service_name):
    if not os.path.isfile('/etc/systemd/system/' + service_name + '.service'):
        print 'operator service:', service_name
        os.system('sudo cp /home/ubuntu/scewpt/etc/systemd/' + service_name + '.service /etc/systemd/system/' + service_name + '.service')
        enable_start(service_name)
    else:
        print service_name, 'is deployed'        

def deferred_sleep(secs):
    return task.deferLater(reactor, secs, defer.succeed, True)    

@defer.inlineCallbacks
def update_dns(region, instance_id):
    print 'update_services:', instance_id
    conn = boto.ec2.connect_to_region(region)
    reservations = conn.get_all_instances(instance_ids=[instance_id])
    instance = reservations[0].instances[0]
    instance.add_tag('Start', int(time.time()))
    try:
        social_env = []
        print 'name:', instance.tags['Name']
        for tagname in [t.strip() for t in instance.tags['Name'].split(',')]:                    
            curator = operate_tag(tagname.strip(), instance)
            if curator:
                yield deferred_sleep(5)
                social_env.append(curator)
        print 'social env length:', len(social_env)        
    except KeyError as ke:
        print 'no tagname name!', ke
    except IndexError as e:
        print 'other error:', e
    print 'complete identify!'
    yield deferred_sleep(1)

def error(err):
    print 'identity exception:', err.__class__.__name__, err
def identify_dns():
    print 'identify_instance'
    dl = defer.DeferredList([identify_service.get_region(), identify_service.get_instance()])
    dl.addCallback(lambda res: update_dns(res[0][1], res[1][1]))
    dl.addErrback(error)
    dl.addBoth(lambda ign: reactor.stop())
    return dl

if __name__ == '__main__':
    reactor.callWhenRunning(identify_dns)
    reactor.run()
