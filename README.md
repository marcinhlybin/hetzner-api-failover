# hetzner-api-failover
Failover script for Hetzner API to be used with keepalived.

Default configuration file path is /etc/keepalived/hetzner.conf. 

## Keepalived configuration:

```
notify_master "/usr/local/sbin/hetzner.py"
```
