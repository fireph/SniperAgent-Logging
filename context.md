# Sniper Context

Context the agent should consider when analyzing logs.

## Ignore

Issues listed here will NOT trigger notifications. Add one entry per line:

- tdarr-server -- "Exit approved. Closing process." is a normal Tdarr shutdown
- authentik-server -- "Error while closing socket [Errno 9] Bad file descriptor" is harmless cleanup during shutdown
- authentik-server -- "websocket: close" and "Worker exiting" are normal Authentik worker lifecycle events
- authentik-server -- "Booting worker with pid" is a normal worker startup, not a problem
- Any error counter with value 0, null, false, or empty (e.g. "error": 0, "failed": 0, "errors": null) is not a real error
- gunicorn.error logger messages are routine server lifecycle events, not real errors
- Any error with websockets closing early or unexpectedly

## Notes

Environment details that help the agent understand what's normal:

- Home lab runs on TrueNAS Scale
- Docker host is the same machine as the log collector
- PFsense is the edge firewall/gateway
