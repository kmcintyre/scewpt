operator = 'operator'
listener = 'listener' 

operator_channels = 'operator_channels'

channel = 'channel'
channel_filter = 'channel_filter'

client_start = 'client_start'
client_first_here = 'first_here'
client_website = 'website'
client_block = 'block'
client_location = 'location'
client_location_latitude = 'latitude' 
client_location_longitude = 'longitude'

instance_job = 'job'
instance_job_command = 'job_command'

websocket_key = 'websocket_key'
websocket_broadcast_type = 'broadcast_type'
websocket_tx = 'websocket_tx'
websocket_rx = 'websocket_rx'
websocket_website = 'websocket_website'
websocket_tx_filtered = 'websocket_tx_filtered'
websocket_connection_init = 'websocket_connection_init'
websocket_ip = 'websocket_ip'
websocket_last_instagram = 'websocket_last_instagram'
websocket_last_facebook = 'websocket_last_facebook'
websocket_ts_connection_last = 'websocket_ts_connection_last'
websocket_ts_start = 'websocket_ts_start'
websocket_ts_end = 'websocket_ts_end'
websocket_cookies = 'websocket_cookies'
websocket_server = 'websocket_server'

def host(h):
    if h.count('.') == 1:
        return h
    elif h.count('.') == 2:
        return h[h.index('.') + 1:]
    else:
        print 'unknown domain:', h
        return h