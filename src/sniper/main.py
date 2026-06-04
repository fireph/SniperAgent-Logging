import asyncio
import threading

from sniper.agent import mcp, run_scan
from sniper.config import Config


def _scheduler_loop():
    cfg = Config.from_env()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        try:
            loop.run_until_complete(run_scan(cfg))
        except Exception:
            pass
        loop.run_until_complete(asyncio.sleep(cfg.scan_interval_hours * 3600))


def main():
    t = threading.Thread(target=_scheduler_loop, daemon=True)
    t.start()
    mcp.run(transport="sse", host="127.0.0.1", port=8080)


if __name__ == "__main__":
    main()
