# Sniper Context

## Ignore

Issues listed here will NOT trigger notifications.

- tdarr-server -- "Exit approved. Closing process." is a normal Tdarr shutdown
- authentik-server -- "Error while closing socket [Errno 9] Bad file descriptor" is harmless cleanup during shutdown
- authentik-server -- "websocket: close" and "Worker exiting" are normal Authentik worker lifecycle events
- authentik-server -- "Booting worker with pid" is a normal worker startup, not a problem
- Any error counter with value 0, null, false, or empty (e.g. "error": 0, "failed": 0, "errors": null) is not a real error
- gunicorn.error logger messages are routine server lifecycle events, not real errors
- Any error with websockets closing early or unexpectedly
- "rss sync didn't cover the period between" is a routine gap in indexer RSS sync, not a real error
- TMDB/TVDB errors (e.g. "Error in TheMovieDb", "TheTVDB") are transient external service issues, not local problems

## Notes

- Home lab runs on TrueNAS Scale
- Docker host is the same machine as the log collector
- PFsense is the edge firewall/gateway
