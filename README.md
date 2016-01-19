# hetzner-api-failover
Failover script for Hetzner API to be used with keepalived.

Keepalived configuration:

```
notify_master "/usr/local/sbin/hetzner.py"
```
