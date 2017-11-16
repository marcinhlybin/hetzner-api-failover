#!/usr/bin/env python
# Script to run keepalived-hetzner.py from cron on MASTER server
# to make sure routing is set up properly
#
# Marcin Hlybin, marcin.hlybin@gmail.com
#
import os
import sys
import argparse
import netifaces

KEEPALIVED_HETZNER_SCRIPT = '/usr/local/sbin/keepalived-hetzner.py'

parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--address', '-a', metavar='IPv4', dest='address', required=True, help='VRRP IP address')
parser.add_argument('--interface', '-i', metavar='IFACE', dest='interface', required=True, help='VRRP interface name')
parser.add_argument('--verbose', '-v', action='store_true', default=False, help='output messages to stdout')
args = parser.parse_args()

interface_addresses = [ n['addr'] for n in netifaces.ifaddresses(args.interface)[netifaces.AF_INET] ]

if args.address in interface_addresses:
    ARGS = ['--exit']
    if args.verbose:
        ARGS.append('--verbose')
        print "MASTER server. Running Hetzner script"
    rc = os.system("{0} {1}".format(KEEPALIVED_HETZNER_SCRIPT, ' '.join(ARGS)))
    sys.exit(os.WEXITSTATUS(rc))
elif args.verbose:
    print "BACKUP server. Not running Hetzner script"

sys.exit(0)
