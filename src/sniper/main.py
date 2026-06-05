import asyncio
import logging
import threading

from sniper.agent import mcp, mcp_ready, run_scan
from sniper.config import Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("sniper")


def _scheduler_loop():
    cfg = Config.from_env()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    log.info("Waiting for MCP server to start before running first scan")
    mcp_ready.wait()
    while True:
        try:
            log.info("Running scheduled log scan")
            result = loop.run_until_complete(run_scan(cfg))
            issues = result.get("issues", [])
            if issues:
                log.info("Scan found %d issue(s)", len(issues))
            else:
                log.info("Scan complete, no issues: %s", result.get("summary", ""))
        except Exception as e:
            log.error("Scan failed: %s", e)
        d, rem = divmod(cfg.scan_interval, 86400)
        h, rem = divmod(rem, 3600)
        m, s = divmod(rem, 60)
        parts = []
        if d:
            parts.append(f"{d} day{'s' if d != 1 else ''}")
        if h:
            parts.append(f"{h} hour{'s' if h != 1 else ''}")
        if m:
            parts.append(f"{m} minute{'s' if m != 1 else ''}")
        if s:
            parts.append(f"{s} second{'s' if s != 1 else ''}")
        log.info("Next scan in %s", " ".join(parts) if parts else "0 seconds")
        loop.run_until_complete(asyncio.sleep(cfg.scan_interval))


def main():
    t = threading.Thread(target=_scheduler_loop, daemon=True)
    t.start()
    mcp.run(transport="sse", host="127.0.0.1", port=8080)


if __name__ == "__main__":
    main()
