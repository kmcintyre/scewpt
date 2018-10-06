import json
import re
import time
from twisted.internet import defer
from twisted.names import client

from twisted.web.template import flattenString

from app import fixed, user_keys
from amazon.dynamo import User, UserAvailable
from services.smtp.template import EmailElement
from app import keys
from amazon import instances, s3

from boto.dynamodb2.table import Table
from boto.dynamodb2.fields import HashKey, RangeKey

from twisted.web.xmlrpc import Proxy

import boto.ec2
from services.smtp import mail_keys

def save_it(derived_from_domain):
    return True

save_domain = ['twitter.com', 'facebook.com', 'instagram.com', 'facebookmail.com', 'mail.instagram.com']

def save_it_agro(derived_from_domain):
    for sd in save_domain:
        if sd in derived_from_domain:
            return True
    return False

class NullBag:

    def get_messages(self):
        return []

    def add_message(self, msg):
        pass

class Postman:

    def __init__(self):
        self.public_dns = 'localhost'
        self.valid_domains = []
        self.invalid_domains = []
        self.routes = []
        self.browser = None
        self.bag = NullBag()

    def resend(self, client, count):
        print 'postman resend'
        for msg in self.bag.get_messages():
            try:
                if not client.cheap_filter(msg):
                    print "re-send message to " + client.peer
                    client.sendMessage(json.dumps(msg))
                    count += -1
                    print 'count:', count
                    if count == 0:
                        return
            except Exception as e:
                print 'resend errror:', e

    def anticipate(self, helo, origin, user):
        print "anticipate count:"
        return EmailElement(helo, origin, user)
        # ee.get_broadcast_dict()

        # anticipate = blank_msg();
        # anticipate['msg'] = 'postman'
        # anticipate['subject'] = 'valid_domains:' + str(self.valid_domains) + "<br/>routes:" + str(self.routes)

        # print "- anticipate tell noone"
        # return "Received"
        # for p in PostOffice.postmen:
        #    p.anticipate()

    def new_email(self, incoming_email, email_element, domain):
        email_element.raw_email(incoming_email)
        email_element.domain = domain

        def error(e):
            print 'new email error:', e

        def add_result_back(html_result):
            if email_element.html is not None:
                try:
                    pattern_obj = re.compile(
                        mail_keys.html_placeholder, re.MULTILINE)
                    html_result = pattern_obj.sub(
                        email_element.html, html_result)
                except Exception as e:
                    print 'bind html exception:', e
            email_element.summary = html_result
            return email_element
        email_element
        d = flattenString(None, email_element)
        d.addCallback(add_result_back)
        d.addCallback(self.broadcast)
        d.addErrback(error)
        return d

    def routeEmail(self, ee):
        print 'broadcast:', ee.get_broadcast_dict()
        print 'route lenth:', len(self.routes)
        for route in self.routes:
            try:
                route.route_email(ee)
            except Exception as e:
                print 'broadcast exception', e

        self.bag.add_message(ee.get_broadcast_dict())
        print 'return ee:', ee
        return ee

    def status(self):
        print 'postman status'
        status = mail_keys.blank_msg()
        status['from'] = 'postman'
        status['subject'] = {'valid_domains': self.valid_domains, 'routes': [
            str(r) for r in self.routes], 'mailbag': str(self.bag)}
        return {'status': status}

    def check_domain(self, domain_name):
        print 'check_domain:', domain_name
        if domain_name == self.public_dns:
            return defer.succeed(True)

        def printresult(records):
            answers, authority, additional = records
            for a in answers:
                print 'a', a.name, a.type, a.fmt, a.payload.name
                try:
                    if str(a.payload.name) == self.public_dns:
                        return True
                except:
                    pass
            return False
        d = client.lookupMailExchange(domain_name)
        d.addCallback(printresult)
        return d

class BrowserPreview:

    def browser_error(self, err):
        import subprocess
        print 'error with browser:', err
        command = ['sudo', 'start', 'browser']
        subprocess.call(command)

    def route_email(self, ee):
        proxy = Proxy('http://localhost:8001/')
        if ee.html:
            print 'preview html in browser'
            d = proxy.callRemote('preview', ee.html, fixed.digest(ee.broadcast_dict['file_dest']))
            d.addCallback(lambda local_file: s3.save_s3(s3.bucket_straight('www.scewpt.com'), str(
                ee.broadcast_dict['file_dest'] + "_preview.png"), None, local_file, "image/png", 'public-read'))
            d.addErrback(self.browser_error)
            return d
        else:
            print 'not previewed'
            return defer.SUCCESS

    def __repr__(self):
        return 'Preview in WebEngine'

class LastLoudestToS3:

    def route_email(self, ee):
        print 'route last/loudest'
        s3.save_s3(s3.bucket_straight('www.scewpt.com'), 'inbox/lastloudest.html', ee.summary, None, 'text/html', 'public-read')

    def __repr__(self):
        return 'Store last/loudest in S3'

class CommandControl:

    def route_email(self, ee):
        from amazon.dynamo import User
        for u in User().scan(username__eq=ee.broadcast_dict['derived_to']):
            print 'CommandControl: email to:', u._data

    def __repr__(self):
        return 'Command/Control'

class PerminentHtmlS3:    

    def route_email(self, ee):
        print 'route email perm'
        if save_it(ee.broadcast_dict['derived_from'].split('@')[-1]):
            s3.save_s3(s3.bucket_straight('www.scewpt.com'), ee.broadcast_dict['file_dest'] + '.html', ee.summary, None, 'text/html', 'public-read')

    def __repr__(self):
        return 'Store Html in S3'

class PerminentJsonS3:

    def route_email(self, ee):
        if save_it(ee.broadcast_dict['derived_from'].split('@')[-1]):
            s3.save_s3(s3.bucket_straight('www.scewpt.com'), ee.broadcast_dict['file_dest'] + '.json', json.dumps(ee.broadcast_dict), None, 'application/json', 'public-read')

    def __repr__(self):
        return 'Store JSON in S3'

class Attachments:

    def route_email(self, ee):
        if save_it(ee.broadcast_dict['derived_from'].split('@')[-1]):
            if ee.attachments is not None:
                for filename, raw_file, content_type in ee.attachments:
                    s3.save_s3(s3.bucket_straight('www.scewpt.com'), ee.broadcast_dict['file_dest'] + "_" + filename, raw_file, None, content_type, 'public-read')
    def __repr__(self):
        return 'Store attachments in S3'
    
class CheckLockedAccount:    

    def route_email(self, ee):
        if ee.broadcast_dict['derived_from'] == 'password@twitter.com' and ee.broadcast_dict['subject'] == 'For security purposes, your Twitter account has been locked.':
            for u in User().query_2(username__eq=ee.broadcast_dict['derived_to']):
                curator = User().get_curator(u[user_keys.user_role])
                instance = u[user_keys.user_role] + '.' + curator[user_keys.user_role]
                inst = instances.get_instances()
                for i in inst:
                    if 'Name' in i.tags:
                        if instance == i.tags['Name']:
                            print 'found instance:', i.id
                            boto.ec2.connect_to_region('us-east-1').reboot_instances([i.id]) 

                
                
    def __repr__(self):
        return 'Store attachments in S3'    

class BagIt:    

    def get_mail_table(self, domain):
        mail_table = 'smtp'
        s3_mail_table = Table(mail_table)
        try:
            print mail_table, 'count:', s3_mail_table.count()
        except:
            print 'creating:', mail_table
            s3_mail_table = Table.create(mail_table,
                                         schema=[
                                             HashKey('derived_to'),
                                             RangeKey('derived_from')
                                         ],
                                         throughput={
                                             'read': 3,
                                             'write': 3
                                         })
        return s3_mail_table

    def route_email(self, ee):
        print 'bag it route_email:', ee.broadcast_dict['derived_to'], 'from:', ee.broadcast_dict['derived_from']
        try:
            item = self.get_mail_table(ee.domain).query(derived_to__eq=ee.broadcast_dict[
                'derived_to'], derived_from__eq=ee.broadcast_dict['derived_from'], limit=1).next()
            item['lastConnection'] = time.time()
            item['connectionsMade'] = item['connectionsMade'] + 1
            item['msg'] = item['msg'] + "," + ee.broadcast_dict['file_dest']
            item.save()
        except Exception as e:
            from boto.dynamodb2.items import Item
            print 'create item:', e
            try:
                now = time.time()
                item = Item(self.get_mail_table(ee.domain),
                            data={
                    'derived_to': ee.broadcast_dict['derived_to'],
                    'derived_from': ee.broadcast_dict['derived_from'],
                    'firstConnection': now,
                    'lastConnection': now,
                    'connectionsMade': 1,
                    'msg': ee.broadcast_dict['file_dest']
                }
                )
                item.save()
            except Exception as e2:
                print e2

    def __repr__(self):
        return 'Store conversation in Dynamo'

class MemoryBag():

    limit = 250

    def __init__(self):
        self.all_msg = []
        self.total_msg = 0

    def get_messages(self):
        return self.all_msg

    def add_message(self, msg):
        self.total_msg += 1
        if msg['derived_from'].split('@')[1] in save_domain:
            if msg['derived_from'].split('@')[1] == 'twitter.com':
                if User().query_count(username__eq=msg['derived_to']) == 0:
                    if UserAvailable().query_count(username__eq=msg['derived_to']) == 0:
                        data = {
                            user_keys.user_username: msg['derived_to'],
                            user_keys.user_type: keys.entity_twitter,
                            user_keys.user_password: 'unknown',
                        }
                        UserAvailable().put_item(data=data)
            if len(self.all_msg) > MemoryBag.limit:
                self.all_msg.pop()
            self.all_msg.insert(0, msg)

    def __repr__(self):
        return 'Memory Only ({0} total)'.format(self.total_msg)