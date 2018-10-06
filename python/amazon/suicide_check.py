import boto.ec2.cloudwatch
from twisted.internet import reactor, defer
import datetime
from amazon import identify_service, provision
import os
import time

def commit_suicide(region, instance_id, tags):
    os.system('sudo /etc/init.d/monit stop')
    conn = boto.ec2.connect_to_region(region)             
    provision.launch_tag(tags)          
    conn.terminate_instances([instance_id])

def run_suicide_check(region, instance_id, reboot = True):
    cpu_balance = get_cpu_balance(instance_id)
    conn = boto.ec2.connect_to_region(region) 
    instance = conn.get_only_instances(instance_ids=[instance_id])[0]
    tags = instance.tags['Name']
    print 'cpu_balance:', cpu_balance, 'tags:', tags, 'region:', region, 'reboot:', reboot
    if cpu_balance is not None and cpu_balance < 2 and reboot and 'Terminating' not in instance.tags:
        instance.add_tag('Terminating', str(int(time.time()))) 
        commit_suicide(region, instance_id, tags)
        
def get_cpu_balance(instance_id):
    try:
        c = boto.ec2.cloudwatch.connect_to_region('us-east-1')
        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(minutes=10)
        data = c.get_metric_statistics(period=300, start_time=start, end_time=end, metric_name='CPUCreditBalance', statistics='Average', namespace='AWS/EC2', dimensions={'InstanceId': instance_id})
        return data[0]['Average']
    except Exception as e:
        return None
    
def error_suicide(err):
    print 'suicide_error:', err
                               
if __name__ == '__main__':
    import sys
    do_reboot = True
    if len(sys.argv) == 1:
        do_reboot = False
    def inline_suicide():
        print 'inline_suicide' 
        dl = defer.DeferredList([identify_service.get_region(), identify_service.get_instance()])
        dl.addCallback(lambda res: run_suicide_check(res[0][1], res[1][1], do_reboot))
        dl.addErrback(error_suicide)
        dl.addBoth(lambda ign: reactor.stop())
        return dl                               
    reactor.callWhenRunning(inline_suicide)
    reactor.run()