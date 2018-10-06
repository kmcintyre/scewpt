from amazon.dynamo import Entity, User
from app import keys, user_keys

from amazon import provision

import boto.ec2
import time
def replacer(upgrade):
    conn=boto.ec2.connect_to_region("us-east-1")
    reservations = conn.get_all_instances()
    for res in reservations:
        for inst in res.instances:
            if inst.state == 'running':
                terminate = False                
                if 'Name' in inst.tags:                    
                    for subres in inst.tags['Name'].split(','):
                        print subres.strip(), upgrade
                        if subres.strip() in upgrade:
                            terminate = True
                            upgrade.remove(subres.strip())
                            print 'terminating:', subres.strip()                        
                if terminate:
                    provision.launch_tag(inst.tags['Name'], completion_delay=120)                
                    conn.terminate_instances([inst.id])
                    time.sleep(30)
                    print 'replace:', inst.tags['Name'], inst.launch_time, inst.id
                    
if __name__ == '__main__':
    import sys                  
    upgrade_all = []
    for league in sorted(Entity().get_leagues(), key=lambda e2: str(e2[keys.entity_league])):
        site = User().get_curator(league[keys.entity_league])[user_keys.user_role]  
        upgrade_all.append(league[keys.entity_league] + '.' + site)    
    
    try:
        replacer([sys.argv[1]])
    except Exception as e:
        print 'huh?:', e
        try:
            print 'update all?:', sys.argv[2]
            #replacer(upgrade_all)
        except:
            print 'nope'
            
    
