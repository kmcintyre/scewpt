import boto.ses
import boto.route53
from app import user_keys
from amazon import emails

import requests
import re

from services import client
from amazon.dynamo import User, UserSuspended, UserAvailable
from twisted.internet import reactor, defer

conn = boto.ses.connect_to_region('us-east-1')

def error(err):
    print 'email error:', err
    reactor.stop()
    
def done():
    print 'email done!'
    reactor.stop()

verified_emails = conn.list_verified_email_addresses()['ListVerifiedEmailAddressesResponse']['ListVerifiedEmailAddressesResult']['VerifiedEmailAddresses']

print 'verified emails:', verified_emails

my_domains = []

for hz in boto.route53.connection.Route53Connection().get_zones():
    my_domains.append(hz.name[:-1])

@defer.inlineCallbacks
def verify():
    print 'verify!'
    for c in  [User, UserSuspended, UserAvailable]:
        for u in c().scan():
            if u[user_keys.user_username].split('@')[1] in my_domains and u[user_keys.user_username] not in verified_emails:
                try:            
                    print 'verify:', u[user_keys.user_username]
                    md = {'filter': {'derived_to': u[user_keys.user_username]}}
                    d = client.mail_listener(mail_domain='mail.scewpt.com', message_filter_dic=md)
                    d.addCallback(client.hearing_back, u[user_keys.user_username])
                    d.addErrback(error)
                    reactor.callLater(1, conn.verify_email_address, u[user_keys.user_username])
                    result = yield d            
                    print 'result:', result['file_dest']
                    html = emails.get_html_from_msg(result['file_dest'])
                    url = re.search('(?P<url>https?://[^\s]+)', html).group('url')            
                    url2 = url.replace('&amp;', '&')
                    r = requests.get(url2)
                    print r.status_code
                except Exception as e:
                    print 'exception:', e                    
    reactor.callLater(2, done)        
                                    
reactor.callWhenRunning(verify)
reactor.run()