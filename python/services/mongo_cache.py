from twisted.internet import reactor
from services.client import start_client, ListenerProtocol  
import sys

if __name__ == '__main__':
    endpoint = 'service.athleets.com'
    if len(sys.argv) > 1:
        endpoint = sys.argv[1]
    class listen():
        start_client(endpoint, ListenerProtocol)
    reactor.callWhenRunning(listen)
    reactor.run()