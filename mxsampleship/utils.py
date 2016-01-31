from six.moves.urllib.parse import urlencode


def arrival_url(dewar):
    query = urlencode([('id', dewar['name']), ('action', 'Arrived')])
    return 'http://10.108.24.6/dewartrack_ipad.php?%s' % query
