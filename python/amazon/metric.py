import boto.ec2.cloudwatch

import datetime

from amazon.dynamo import User

from app import keys

dynamo_metric_name = 'ConsumedWriteCapacityUnits'

def leagues_sorted_2(ts):
    print 'leagues_sorted:', ts
    user_leagues = User().get_leagues()
    return sorted(user_leagues, key=lambda item: item[ts])

def epoch_time(dt):
    tm = dt - datetime.timedelta(minutes=dt.minute %
                                 10, seconds=dt.second, microseconds=dt.microsecond)
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = tm - epoch
    return delta.total_seconds()


def instance_metric_ec2(instance_id, metric_name, metric_range = (300, 600)):
    c = boto.ec2.cloudwatch.connect_to_region('us-east-1')
    return [m for m in c.get_metric_statistics(
        metric_range[0],
        datetime.datetime.now() - datetime.timedelta(seconds=metric_range[1]),
        datetime.datetime.now(),
        metric_name,
        'AWS/EC2',
        'Average',
        dimensions={'InstanceId':[instance_id]}
    )]

def tweets_json(index='in_league'):
    return dynamo_json('tweet_next', index, 'Tweets 15 Minute Average')


def retweets_json(index='in_league'):
    return dynamo_json('retweet', index, 'Retweets 15 Minute Average')

def dynamo_json(table_name, index_name, chart_metric=None, average_period=900):
    end = datetime.datetime.utcnow()
    start = end - datetime.timedelta(days=3)
    c = boto.ec2.cloudwatch.connect_to_region('us-east-1')
    data = c.get_metric_statistics(period=average_period, start_time=start, end_time=end,
                                   metric_name=dynamo_metric_name,
                                   namespace='AWS/DynamoDB',
                                   statistics=['Sum'],
                                   dimensions={
                                       'TableName': table_name, 'GlobalSecondaryIndexName': index_name}
                                   )
    print 'data length:', len(data)
    for d in data:

        d['chart_ts'] = int(epoch_time(d['Timestamp']))
        d['chart_metric'] = chart_metric
        d[keys.entity_league] = 'all'
        d['chart_value'] = d['Sum']
        del d['Timestamp']
    data.sort(key=lambda key: key['chart_ts'], reverse=True)
    if chart_metric and data:
        for save_d in data:
            try:
                copy_save_d = save_d.copy()
                ans = Chart().put_item(data=copy_save_d)
                print 'chart metric saved:', ans, copy_save_d
            except Exception as e:
                print 'chart put item exception:', e, save_d
                break
    return data