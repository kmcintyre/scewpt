from amazon.dynamo import Tweet

import time

all_keys = set([])
all_keys_count = 0
for e in Tweet().scan():
    for k in e._data.keys():
        all_keys.add(k)
        if len(all_keys) > all_keys_count:
            all_keys_count = len(all_keys)
            print ''
            print sorted(list(all_keys))
            print ''
    time.sleep(.25)