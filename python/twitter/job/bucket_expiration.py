import boto
from amazon.dynamo import User
from app import user_keys

s3 = boto.connect_s3()

for u in User().get_sites():
    from boto.s3.lifecycle import (
        Lifecycle,
        Expiration,
    )    
    bucket = s3.get_bucket(u[user_keys.user_role])
    bucket.delete_lifecycle_configuration()
    lifecycle = Lifecycle()
    for l in u[user_keys.user_site_leagues]:        
        lifecycle.add_rule(
             l + ' tweets expire',
             prefix= l + '/tweet',
             status='Enabled',
             expiration=Expiration(days=7)
        )    
    
    bucket.configure_lifecycle(lifecycle)
    