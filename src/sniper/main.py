import asyncio
import logging
import threading

from sniper.agent import mcp, run_scan
from sniper.config import Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("sniper")


def _scheduler_loop():
    cfg = Config.from_env()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
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
        log.info("Next scan in %d hours", cfg.scan_interval_hours)
        loop.run_until_complete(asyncio.sleep(cfg.scan_interval_hours * 3600))


def main():
    t = threading.Thread(target=_scheduler_loop, daemon=True)
    t.start()
    mcp.run(transport="sse", host="127.0.0.1", port=8080)


if __name__ == "__main__":
    main()
