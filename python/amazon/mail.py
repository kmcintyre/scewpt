from boto.dynamodb2.table import Table
import boto
import time

mail_table_prefix = 'mail_'
mail_bucket_prefix = 'mail.'

from s3 import bucket_util

s3_conn = boto.connect_s3()


def mail_table(domain_name):
    if domain_name.startswith(mail_table_prefix):
        print 'mail_table:', domain_name
        mt = Table(domain_name)
        print 'mail_table count:', mt.count()
        return mt
    else:
        return mail_table(mail_table_prefix + domain_name)


def mail_bucket(domain_name):
    print 'mail_bucket'
    if domain_name.startswith('mail.'):
        domain_name = domain_name[5:]
    print 'mail domain:', domain_name
    return bucket_util.subdomain_bucket('mail', domain_name)


def msg(domain_name, msg):
    print 'retrieve message:', msg
    if '.' not in msg:
        msg += '.html'
    print 'msg for-real:', msg
    real_msg = mail_bucket(domain_name).get_key(msg)
    print 'real_msg', real_msg
    return real_msg


def messages(domain_name, derived_to, filters_list=[], sort_list=[]):
    print 'messages'
    msg_list = []
    try:
        print 'derived_to:', derived_to
        all_mg_convs = mail_table(domain_name).scan(derived_to__eq=derived_to)
        for item in all_mg_convs:
            print 'from conversations:', item['derived_from'], ' last connection:', time.ctime(item['lastConnection']), 'conversation length:', len(item['msg'].split(","))
            try:
                for msg in reversed(item['msg'].split(",")):
                    # bl = default_mail_bucket.default_bucket.list(prefix=msg)
                    print 'msg split:', msg
                    msg_list.append(msg)
            except Exception as e:
                print 'messages failure:', e
    except Exception as e:
        print 'mail error:', e

    if sort_list:
        [sorted(msg_list, key=sorter) for sorter in sort_list]
    if filters_list:
        for filter_fn in filters_list:
            filter(filter_fn, msg_list)
    return msg_list