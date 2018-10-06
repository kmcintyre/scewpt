import os

from app import communication_keys

from amazon import suicide_check
from amazon.sqs import WorkerQueue
from amazon.suicide_check import get_cpu_balance
from twisted.web.client import getPage

from twisted.web import xmlrpc, server
from twisted.internet import defer, reactor

import StringIO
import subprocess
import json
import boto.ec2

lock_apk = defer.DeferredLock()
from twisted.internet import protocol

processes = []

class SpawnProcessProtocol(protocol.ProcessProtocol):

    def outReceived(self, data):
        print 'data:', data

    def errReceived(self, data):
        print "errReceived! with %d bytes!" % len(data)
        print 'data:', data
        
    def errConnectionLost(self):
        processes.remove(self)
        print 'connection lost:', len(processes)

class LeagueWorker(xmlrpc.XMLRPC):
    
    @defer.inlineCallbacks
    def xmlrpc_html(self, url, delay = 0):
        yield subprocess.call(['python', 'pyscewpt/xmlrpc/scrape.py', url, '/tmp/scrape.html', str(delay)])
        with open('/tmp/scrape.html', 'r') as readfile:
            io = StringIO.StringIO(readfile.read()).getvalue()
            defer.returnValue(io)
                            
    def xmlrpc_spawn(self, script, path):
        if len(processes) < 10:                
            command_list = ['/usr/bin/python', script] + path.split()        
            print  'command_list:', command_list
            pythonpath = '/home/ubuntu/scewpt'
            env = {}
            env['PYTHONPATH'] = pythonpath
            env['PYTHONIOENCODING'] = 'utf8'
            spp = SpawnProcessProtocol()
            
            processes.append(spp)                      
            reactor.spawnProcess(spp, command_list[0], args=command_list, env=env, path=pythonpath)
            print 'spawn called'        
            return True 
        else:
            return False

    @defer.inlineCallbacks
    def do_build(self, lg, site, league, apk):
        pack = '.'.join([site.split('.')[1],site.split('.')[0],league]) 
        print 'pack:', pack
        yield subprocess.check_call(['/bin/bash', '/home/ubuntu/scewpt/etc/bin/apk/apk.sh', lg, pack])        
        
    @defer.inlineCallbacks
    def sign_build(self, site, league, apk):        
        yield subprocess.check_call(['/bin/bash', '/home/ubuntu/scewpt/etc/bin/apk/create_keystore.sh', site, league])        
        yield subprocess.check_call(['/bin/bash', '/home/ubuntu/scewpt/etc/bin/apk/sign_apk.sh', site, league, apk])
        yield subprocess.check_call(['/bin/bash', '/home/ubuntu/scewpt/etc/bin/apk/zip_apk.sh', site, league, apk])
        
    @defer.inlineCallbacks
    def xmlrpc_build(self, site, league, apk):
        print 'build:', lock_apk.locked
        directory = '/home/ubuntu/' + site + '/' + league + '/app'        
        if not os.path.exists(directory):
            os.makedirs(directory)                
        lg = '/home/ubuntu/' + site + '/' + league + '/app/' + apk + '.apk'
        print 'latest greatest destination:', lg                
        d = lock_apk.run(self.do_build, lg, site, league, apk)
        build_response = yield d
        print 'build response:', build_response, lock_apk.locked                        
        sign_response = yield self.sign_build(site, league, apk)
        print 'sign response:', sign_response
        defer.returnValue(sign_response)
    

    @defer.inlineCallbacks
    def xmlrpc_job(self, job_command, instance_id, message_id):
        print 'job_command:', job_command 
        try:
            stdout = yield subprocess.check_call(job_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            print 'xmlrpc_job:', stdout
        finally:
            conn = boto.ec2.connect_to_region('us-east-1')
            myself = conn.get_only_instances(instance_ids=[instance_id])[0]
            myself.remove_tag('Work')        
        
    @defer.inlineCallbacks 
    def worker_check(self):
        loop_delay = 180
        print 'worker_check!:', loop_delay
        dl = defer.DeferredList([
            getPage('http://169.254.169.254/latest/meta-data/instance-id'),
            getPage('http://169.254.169.254/latest/meta-data/placement/availability-zone')
        ])
        inst_reg = yield dl
        if inst_reg[0][0] and inst_reg[1][0]:
            instance_id, region = inst_reg[0][1], inst_reg[1][1]
            conn = boto.ec2.connect_to_region('us-east-1')
            suicide_check.run_suicide_check('us-east-1', instance_id, True)
            myself = conn.get_only_instances(instance_ids=[instance_id])[0]
            balance = get_cpu_balance(instance_id)
            
            print 'instance_id:', instance_id, 'region:', region, 'balance:', balance
            
            print myself.tags['Name'], 'instance_id:', instance_id, 'balance:', balance, 'region:', region
            if balance and int(balance) > 50:
                try:
                    current_job = myself.tags['Work']
                    print 'current job:', current_job
                    job = WorkerQueue().getMessage()
                    if current_job == 'ready' or job.id == current_job:                         
                        json_job = json.loads(job.get_body())
                        print job.id, json_job[communication_keys.instance_job], json_job[communication_keys.instance_job_command]                    
                        myself.add_tag('Work', job.id)                                    
                        self.xmlrpc_job(json_job[communication_keys.instance_job_command], instance_id, job.id)                    
                        WorkerQueue().deleteMessage(job) 
                except AttributeError:
                    myself.add_tag('Work','ready')
                    pass
                except KeyError as e:
                    print 'not working!'
                    myself.add_tag('Work','ready')
            elif balance is None:
                print 'no balance'
            elif 'Work' in myself.tags:
                print 'am working need to quit:', myself.tags['Work'] 
                myself.remove_tag('Work')
            else:
                print 'am resting'
            reactor.callLater(loop_delay, lw.worker_check)                                        
        else:              
            print 'offsite!'
        

if __name__ == '__main__':
    lw = LeagueWorker(allowNone=True)
    reactor.callWhenRunning(lw.worker_check)     
    reactor.listenTCP(7080, server.Site(lw))
    reactor.run()
