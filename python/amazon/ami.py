from twisted.internet import reactor, defer, task
from amazon import identify_service

import boto.ec2
import sys

from app import keys

@defer.inlineCallbacks
def region_instance(region_instance_seq, version):
    print region_instance_seq
    print 'ans:', region_instance_seq[0], region_instance_seq[1]
    conn = boto.ec2.connect_to_region(region_instance_seq[0])
    for image in conn.get_all_images(owners=['self'], filters={'name': version }):
        try:
            print 'de-register images:', image
            image.deregister()
        except Exception as e:
            print 'de-register error:', e
    yield task.deferLater(reactor, 60, defer.succeed, True)
    print 'create image:', version
    conn.create_image(region_instance_seq[1], version)

def ami(version):
    dl = defer.DeferredList([identify_service.get_region(), identify_service.get_instance()])
    dl.addCallback(lambda res: defer.succeed((res[0][1], res[1][1])))
    dl.addCallback(region_instance, version)

if __name__ == '__main__':
    v = keys.v2
    if len(sys.argv) > 1:
        v = sys.argv[1]
    reactor.callWhenRunning(ami, v)
    reactor.run()
