import logging
import boto3
import json
import decimal
import datetime
import time

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class SetEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, datetime.datetime):
            return int(time.mktime(obj.timetuple()))
        elif isinstance(obj, decimal.Decimal):
            return int(obj)
        return json.JSONEncoder.default(self, obj)
    
def lambda_handler(event, context):
    dynamodb = boto3.resource("dynamodb", region_name='us-east-1')
    table = dynamodb.Table('profile_twitter')    
    try:
        response = table.get_item(
            Key={
                'twitter_id': event['twitter_id'],
                'ts_add': event['ts_add']
            }
        )
        logger.info('response: {}'.format(response['Item']))
        return {
            "statusCode": 200,
            "body": json.dumps(response['Item'], indent=4, cls=SetEncoder)
        }        
    except ClientError as e:
        return e.response['Error']['Message']
    except Exception as e:
        return 'exception:', e

    
if __name__ == '__main__':
    logger.addHandler(logging.StreamHandler())
    lambda_handler({'twitter_id': '108042166', 'ts_add': 1519422896}, None)
    