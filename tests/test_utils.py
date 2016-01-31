from mxsampleship.utils import arrival_url


def test_arrival_url():
    url = arrival_url({'name': '123'})
    assert url == 'http://10.108.24.6/dewartrack_ipad.php?id=123&action=Arrived'
