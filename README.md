# Keepalived Hetzner API

Keepalived failover script for Hetzner API

## Usage

Copy `keepalived-hetzner.py` to `/usr/local/sbin/keepalived-hetzner.py`.
Install pip packages from `requirements.txt`: `pip install -r requirements.txt`

```
usage: keepalived-hetzner.py [-h] [--config CONFIG] [--exit] [--debug]

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        config file (default: /etc/keepalived/hetzner.conf)
  --exit, -e            exit on error immediately (default: False)
  --debug, -d           output messages to stdout (default: False)
```

By default the script writes to syslog (`/var/log/syslog`). Use `--debug` to print message to stdout.

Configuration file path is /etc/keepalived/hetzner.conf. Use `--config` to set different path.

This software tries really hard to make failover. If it fails for whatever reason, it tries every minute again and again. It exits only if failover is confirmed or number of retries is hit (1000). Use `--exit` to exit immediately after error. Especially useful for debugging.

If you spot any errors or uncaught exceptions please open an issue on github.

## Configuration

### /etc/keepalived/keepalived.conf

Add following line to your `keepalived.conf`:

```
notify_master "/usr/local/sbin/keepalived-hetzner.py"
```

### /etc/keepalived/hetzner.conf

See sample file `hetzner-sample.conf`.

You can specify many failover addresses separated by comma in `failover_address` config option. The script will fork as many times as addresses you put there. Notice that you may exceed process limit or Hetzner's API requests limit.
