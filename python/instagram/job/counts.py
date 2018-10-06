from amazon.dynamo import Entity


c = 0
for e in Entity().scan(instagram__null=False):
    c += 1
print 'instagram count:', c