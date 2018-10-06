from amazon.dynamo import Connection
from app import communication_keys

import time

yesterday = int(time.time()) - (24 * 60 * 60)

for c in Connection().scan(websocket_ts_start__gt=yesterday):
    if c[communication_keys.websocket_ip] != '73.231.191.195' and '10.0.0' not in c[communication_keys.websocket_ip]:
        print c[communication_keys.websocket_ip], c[communication_keys.websocket_website]