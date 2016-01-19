import unittest
import grequests
import sys
from StringIO import StringIO
from hetzner import Hetzner

class HetznerMock(Hetzner):
    def failover_requests(self):
        urls = [
            'https://httpbin.org/status/200',
            'https://httpbin.org/status/200',
            'https://httpbin.org/status/500',
        ]
        for url in urls:
            yield grequests.post(url)

class TestHetzner(unittest.TestCase):
    def test_server_address(self):
        self.assertEqual(hetzner.server_address, '8.8.8.8')

    def test_server_host(self):
        self.assertEqual(hetzner.server_host, 'google-public-dns-a.google.com')

    def test_failover_addresses(self):
        self.assertEqual(hetzner.failover_addresses[1], '5.6.7.8')

    def test_api_url(self):
        self.assertEqual(hetzner.api_url, 'https://robot-ws.your-server.de')

    def test_api_user(self):
        self.assertEqual(hetzner.api_user, 'API_USER')

    def test_api_password(self):
        self.assertEqual(hetzner.api_password, 'API_PASSWORD')

    def test_url(self):
        self.assertEqual(hetzner.url, 'https://robot-ws.your-server.de/failover/')

    def test_failover(self):
        expected_output = """
INFO Hetzner route 1.2.3.4 to 8.8.8.8 [google-public-dns-a.google.com] started
INFO Hetzner route 1.2.3.4 to 8.8.8.8 [google-public-dns-a.google.com] finished successfully
INFO Hetzner route 5.6.7.8 to 8.8.8.8 [google-public-dns-a.google.com] started
INFO Hetzner route 5.6.7.8 to 8.8.8.8 [google-public-dns-a.google.com] finished successfully
INFO Hetzner route 9.10.11.12 to 8.8.8.8 [google-public-dns-a.google.com] started
ERROR Hetzner route 9.10.11.12 to 8.8.8.8 [google-public-dns-a.google.com] failed
"""
        sys.stdout = StringIO()
        hetzner.failover()
        self.assertEquals(sys.stdout.getvalue().strip(), expected_output.strip())

hetzner = HetznerMock(config='hetzner-sample.conf', syslog=False)
unittest.main()
