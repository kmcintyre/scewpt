_placeholder = '_place_holder_'
html_placeholder = '<span>' + _placeholder + '</span>'

email_filename = '(.*?)"(.*?)"'

ds_format = '%Y_%m_%d'
dt_format = ds_format + '/%H_%M_%S'
dt_single_format = '%Y_%m_%d_%H_%M_%S'

NO_SUBJECT = "(no subject)"

version = 'm2'

def sizeof_fmt(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def blank_msg():
    return {
        'msg': None,
        'derived_to': None,
        'derived_from': None,
        'to': None,
        'from': None,
        'subject': None,
        'helo': None,
        'attachments': None,
        'multipart': None,
        'origin': None,
        'user': None,
        'date': None
    }
