from twisted.web.client import getPage
from twisted.internet import reactor

import boto.ec2

def get_instance():
    print 'get_instance!'
    d = getPage('http://169.254.169.254/latest/meta-data/instance-id')
    return d

def parse_region(region):
    for r in boto.ec2.regions():
        if r.name in region:
            return r.name

def get_region():
    print 'get_region!'
    d = getPage('http://169.254.169.254/latest/meta-data/placement/availability-zone')    
    d.addCallback(parse_region)
    return d

if __name__ == '__main__':
    reactor.run()
