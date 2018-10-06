import boto.ec2
from amazon import suicide_check

def get_tag_name(a):
    try: 
        return a.tags['Name']
    except:
        return 'untagged'
    
def print_instance(a):
    if a.state not in ['terminated']: 
        print '%22s' % a.id, '%20s' % str(a.launch_time).replace('T', ' ').rsplit(':', 1)[0], '%10s' % a.instance_type, '%16s' % a.ip_address, '%11s' % a.state, '%30s' % get_tag_name(a), '%5s' % suicide_check.get_cpu_balance(a.id)

def get_images():
    images = []
    conn = boto.ec2.connect_to_region('us-east-1')
    for image in conn.get_all_images(owners=['self']):        
        images.append(image)
    return images    

def get_instance(instance_id):
    conn = boto.ec2.connect_to_region('us-east-1')
    return [instance for instance in conn.get_only_instances(instance_ids=[instance_id])][0]

def get_instances(filter_by={}, sort_by='name'):
    print sort_by
    instances = []        
    for region in [r for r in boto.ec2.regions() if r.name == 'us-east-1']:
        conn = boto.ec2.connect_to_region('us-east-1')
        print 'region:', region.name    
        for instance in conn.get_only_instances(filters=filter_by):
            try:
                instances.append(instance)                
            except boto.exception.EC2ResponseError as e:
                print 'ec2 response error:', e.status, instance
            except Exception as e:
                print 'instance exception:', e, instance
        if sort_by == 'name':
            instances.sort(key=lambda inst: get_tag_name(inst))                                            
        elif sort_by == 'launch':
            instances.sort(key=lambda inst: inst.launch_time)                                            
        
    return instances

if __name__ == '__main__':
    import sys
    sb = 'name'
    if len(sys.argv) > 1:
        sb = sys.argv[1]
    for image in get_images():
        print 'images:', image
    print '    '                    
    for a in get_instances({}, sb):
        print_instance(a)
