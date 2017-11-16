#!/usr/bin/env python
# Keepalived failover script for Hetzner API
#
# Set in keepalived.conf:
# notify_master "/usr/local/sbin/keepalived-hetzner.py"
#
# Marcin Hlybin, marcin.hlybin@gmail.com
#
import argparse
import socket
import os
import sys
import time
import requests
import json
import syslog as s
from configobj import ConfigObj

CONFIG_FILE = '/etc/keepalived/hetzner.conf'
RETRY_TIMES = 1000
CONNECTION_TIMEOUT = 300
STATUS_OK = 200
STATUS_ALREADY_ROUTED = 409
CONFIG_OPTIONS = (
    'server_address',
    'failover_address',
    'api_url',
    'api_user',
    'api_password'
)

def log(message):
    s.syslog(message)
    if args.verbose:
        print message

def read_config(config_file):
    if not os.path.exists(config_file):
        log("ERROR: Hetzner failover failed: config file '{}' not found".format(config_file))
        sys.exit(1)

    config = ConfigObj(config_file)

    for option in CONFIG_OPTIONS:
        if not config.get(option):
            log("ERROR: Hetzner failover failed: option '{}' is required".format(option, config_file))
            sys.exit(1)

    try:
        config['server_host'] = socket.gethostbyaddr(config['server_address'])[0]
    except:
        config['server_host'] = None

    if type(config['failover_address']) is not list:
        config['failover_address'] = [config['failover_address']]

    return config

def request(failover_address):
    retry = 0
    while retry < RETRY_TIMES:
        params = { 'active_server_ip': c['server_address'] }
        headers = { 'content-type': 'application/json' }
        auth = (c['api_user'], c['api_password'])
        url = c['api_url'] + '/failover/' + failover_address
        failover_requested = False
        try:
            r = requests.post(url, params=params, headers=headers, auth=auth, timeout=CONNECTION_TIMEOUT)
            res = r.json()
            if r.status_code == STATUS_OK:
                log("Hetzner failover requested: {} -> {} [{}]".format(failover_address, c['server_address'], c['server_host']))
                failover_requested = True
                time.sleep(30)
                continue
            elif r.status_code == STATUS_ALREADY_ROUTED and res['error']['code'] == 'FAILOVER_ALREADY_ROUTED':
                if failover_requested:
                    log("Hetzner failover finished: {} -> {} [{}]".format(failover_address, c['server_address'], c['server_host']))
                break
            elif r.status_code == STATUS_ALREADY_ROUTED:
                log("Hetzner failover in progress: {} -> {} [{}]".format(failover_address, c['server_address'], c['server_host']))
                time.sleep(30)
                continue
            else:
                error_message = res.get('error', {}).get('message') or 'Connection error'
                log("ERROR: Hetzner failover failed: {} -> {} [{}]: {}".format(failover_address, c['server_address'], c['server_host'], error_message))
                if args.exit:
                    # OS exit to not raise exception
                    os._exit(1)
                time.sleep(60)
        except Exception, e:
            log("ERROR: Hetzner failover failed: {} -> {} [{}]: Exception raised: {}".format(failover_address, c['server_address'], c['server_host'], str(e)))
            if args.exit:
                sys.exit(1)
            time.sleep(60)
            pass
        retry += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--config', '-c', dest='config', default=CONFIG_FILE, help='config file')
    parser.add_argument('--exit', '-e', action='store_true', default=False, help='exit on error immediately')
    parser.add_argument('--verbose', '-v', action='store_true', default=False, help='output messages to stdout')
    args = parser.parse_args()

    c = read_config(args.config)

    for failover_address in c['failover_address']:
        try:
            pid = os.fork()
            if pid > 0:
                request(failover_address)
                break
        except OSError, e:
            log("ERROR: Hetzner failover failed: {} -> {} [{}]: Fork failed".format(failover_address, c['server_address'], c['server_host']))
            sys.exit(1)
