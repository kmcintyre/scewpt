import boto3

#client = boto3.client('apigateway')
userTable = boto3.resource('dynamodb', 'us-east-1').Table('Test')
print 'userTable:', userTable
userData = {'username': 'username'}
user = userTable.get_item(Key=userData)
if 'Item' in user:
    print 'found:', user['Item']
else:
    print 'missing'
    ans = userTable.put_item(Item=userData)
    print 'ans:', ans
    