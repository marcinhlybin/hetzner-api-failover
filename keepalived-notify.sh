#!/bin/bash
# The script saves keepalived instance state to the file
#
mkdir -m 0700 -p /var/run/keepalived
rm -f /var/run/keepalived/*.state
echo $1 $2 is in $3 state > /var/run/keepalived/$2.state
