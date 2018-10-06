import boto.ec2.cloudwatch
import datetime
import json

from amazon.dynamo import User
from app import user_keys
from amazon import s3 

c = boto.ec2.cloudwatch.connect_to_region('us-east-1')

end = datetime.datetime.utcnow()
start = end - datetime.timedelta(days=14)

epoch = datetime.datetime.utcfromtimestamp(0)
average_period=900

data = c.get_metric_statistics(period=average_period, start_time=start, end_time=end,
   metric_name='ConsumedWriteCapacityUnits',
   namespace='AWS/DynamoDB',
   statistics=['Sum'],
   dimensions={
       'TableName': 'tweet'
   }
)
print 'data length:', len(data)

social_sum = [{ 'timestamp' : int((d['Timestamp'] - epoch).total_seconds()), 'sum': int(d['Sum']) } for d in data]
for site in User().get_sites():
    s3.save_s3(
        s3.bucket_straight(site[user_keys.user_role]),
        'chart/social.json',
        json.dumps(social_sum),
        None,
        'application/json',
        'public-read'
    )