#!/usr/bin/env python
#
# Hetzner API Failover script for keepalived
#
# Keepalived configuration:
# notify_master "/usr/local/sbin/hetzner.py"
#
# Marcin Hlybin, ahes@sysadmin.guru
#
import json
import syslog as s
import socket
import sys
import grequests
from configobj import ConfigObj

CONFIG_FILE = '/etc/keepalived/hetzner.conf'

class Hetzner:
    def __init__(self, config, syslog=True):
        try:
            c = ConfigObj(config, list_values=True)

            self.server_address = c.get('server_address')
            self.server_host = socket.gethostbyaddr(self.server_address)[0]

            self.failover_addresses = c.get('failover_address')
            if type(self.failover_addresses) is not list:
                self.failover_addresses = [self.failover_addresses]

            self.api_url = c.get('api_url')
            self.api_user = c.get('api_user')
            self.api_password = c.get('api_password')
            self.url = self.api_url + '/failover/'
            self.syslog = syslog
        except:
            print "Error reading configuration file {}".format(config)
            sys.exit(1)

    def failover(self):
        reqs = self.failover_requests()
        for idx, req in enumerate(grequests.map(reqs)):
            failover_address = self.failover_addresses[idx]
            self.print_message("INFO Hetzner route {} to {} [{}] started".format(failover_address, self.server_address, self.server_host))
            if req.status_code != 200:
                try:
                    res = json.loads(req.content)
                    self.print_message("ERROR Hetzner route {} to {} [{}]: {} -- {}".format(failover_address, self.server_address, self.server_host, res['error']['status'], res['error']['message']), error=True)
                except ValueError:
                    self.print_message("ERROR Hetzner route {} to {} [{}] failed".format(failover_address, self.server_address, self.server_host), error=True)
            else:
                self.print_message("INFO Hetzner route {} to {} [{}] finished successfully".format(failover_address, self.server_address, self.server_host))

    def print_message(self, message, error=False):
        if self.syslog and error:
            s.syslog(syslog.LOG_ERR, message)
        elif self.syslog and not error:
            s.syslog(message)
        else:
            print message

    def failover_requests(self):
        params = { 'active_server_ip': self.server_address }
        headers = { 'content-type': 'application/json' }
        auth = (self.api_user, self.api_password)

        for failover_address in failover_addresses:
            url = self.api_url + '/failover/' + failover_address
            yield grequests.post(url, params=params, headers=headers, auth=auth)

if __name__ == '__main__':
    hetzner = Hetzner(CONFIG_FILE)
