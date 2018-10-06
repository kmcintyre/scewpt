import sys

from amazon.dynamo import User, Entity

def publish_program(host, program):
    import boto
    c = boto.connect_cloudfront()
    for d in c.get_all_distributions():
        if d.origin.dns_name == host:
            print 'good'
        else:
            print 'bad', d.origin.dns_name


def do_invalidate(paths, origin):
    print 'do invalidate'
    import boto
    c = boto.connect_cloudfront()
    for d in c.get_all_distributions():
        print 'distribution:', d.origin.dns_name, d.cnames, origin
        if d.cnames[0] == str(sys.argv[1]):
            print d.id, d.domain_name, d.status, d.comment
            for ir in c.get_invalidation_requests(d.id):
                if ir.status != 'Completed':
                    return 'no can do!!!'
                    print 'invalidate request:', ir.id, ir.status
            print 'create invalidation'
            c.create_invalidation_request(d.id, paths)

if __name__ == '__main__':
    cf = str(sys.argv[1]) + '.s3.amazonaws.com'
    print 'cloudfront:', cf
    standard_file = ['/*']
    print 'standard_file:', standard_file
    do_invalidate(standard_file, cf)
