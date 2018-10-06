from amazon import identify_service
import boto.ec2

import time

from twisted.internet import defer

@defer.inlineCallbacks
def reboot(tags = {}):
    try:
        conn=boto.ec2.connect_to_region("us-east-1")
        instance_id = yield identify_service.get_instance()
        print 'instance_id:', instance_id    
        instance = conn.get_only_instances(instance_ids=[instance_id])[0]
        instance.add_tag('Reboot', int(time.time()))
        for k in tags.keys():
            instance.add_tag(k, tags[k])
        conn.reboot_instances([instance_id])
    except Exception as e:
        print 'reboot exception:', e
    
if __name__ == '__main__':
    from twisted.internet import reactor  
    reactor.callWhenRunning(reboot)
    reactor.run()
    