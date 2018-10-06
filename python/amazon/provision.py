import time
import sys

import boto.ec2
from boto.vpc import VPCConnection

from app import keys, user_keys

def get_size(tn):
    print 'get size:', tn
    if tn in ['match', 'service']:
        return 't2.micro'
    elif tn in ['following', 'bible']:
        return 't2.small'    
    elif tn in ['mail']:
        return 't2.nano'
    else:        
        return 't2.micro'

def launch_tag(tag_name, version = keys.v2, reservation_delay = 5, pending_delay = 5, completion_delay = 180):    
    print 'launch_tag:', tag_name
    conn = boto.ec2.connect_to_region("us-east-1")

    worker_id = [sg.id for sg in conn.get_all_security_groups() if sg.name == 'worker'][0]
    print 'security group:', worker_id
    
    image_id = conn.get_all_images(owners=['self'], filters={'name': version})[0].id
    print 'ami:', image_id
    
    subnet_id = VPCConnection().get_all_subnets()[0].id
    print 'subnet:', subnet_id
    
    interface = boto.ec2.networkinterface.NetworkInterfaceSpecification(
        subnet_id=subnet_id,
        groups=[worker_id],
        associate_public_ip_address=True
    )
    
    interfaces = boto.ec2.networkinterface.NetworkInterfaceCollection(interface)
    
    _it = get_size(tag_name)
    
    print 'instance type:', _it
    
    reservation = conn.run_instances(
        image_id=image_id,
        instance_type=_it,
        network_interfaces=interfaces,
        key_name='lucid'
    )
    print 'reservation:', reservation
    time.sleep(reservation_delay)
    instance = reservation.instances[0]
    print 'instance:', instance
    instance.add_tag("Name", tag_name)
    instance.update()
    print 'update tag Name:', tag_name
    while instance.state == "pending":
        print 'instance state:', instance, instance.state
        time.sleep(pending_delay)
        instance.update()
    print 'launch done', instance
    time.sleep(completion_delay)    

if __name__ == '__main__':    
    from amazon.dynamo import Entity, User
    group_max = 1
    def identify_instance():
        leagues = sorted(Entity().get_leagues(), key=lambda e2: str(e2[keys.entity_league]))
        groups = []
        for league in leagues:
            if len(groups) < group_max:
                groups.append(league)
            if len(groups) == group_max:
                tn = ', '.join(
                    [l[keys.entity_league] + '.' + User().get_curator(l[keys.entity_league])[user_keys.user_role] for l in groups])
                launch_tag(tn)
                groups = []
        if groups:
            tn = ', '.join(
                [l[keys.entity_league] + '.' + User().get_curator(l[keys.entity_league])[user_keys.user_role] for l in groups])
            launch_tag(tn)
    if len(sys.argv) == 1:
        identify_instance()
    else:
        launch_tag(sys.argv[1])
