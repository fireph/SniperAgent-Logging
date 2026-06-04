# Sniper Context

Edit this file to add context the agent should consider when analyzing logs.

## Ignore

Issues listed here will NOT trigger notifications. Add one entry per line:

- Example: certbot renewal failures on port 80 are expected during off-hours
- Example: pfsense gateway alarm on WAN1 is a known ISP issue

## Notes

Environment details that help the agent understand what's normal:

- Home lab runs on TrueNAS Scale
- Docker host is the same machine as the log collector
- PFsense is the edge firewall/gateway
