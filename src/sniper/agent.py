import json
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan as _lifespan
from openai import AsyncOpenAI

from sniper.config import Config
from sniper.context import load_context
from sniper.notifier import SEVERITY_PRIORITY, send_gotify

mcp_ready = threading.Event()


@_lifespan
async def _server_lifespan(server):
    mcp_ready.set()
    yield


mcp = FastMCP("sniper-agent", lifespan=_server_lifespan)

SYSTEM_PROMPT = """You are a log analysis agent. Given log entries and context, identify issues that require attention.

The user-provided context markdown contains an "## Ignore" section listing issues that should NOT be flagged, and a "## Notes" section with environment details. Respect both.

Classify severity as one of:
- "info": informational, no action needed
- "low": minor issue, can wait
- "medium": moderate issue, should address soon
- "high": significant issue, needs prompt attention
- "urgent": critical, needs immediate action

Return a JSON object:
{
  "issues": [
    {
      "severity": "medium",
      "source": "container_name or pfsense",
      "title": "Brief title",
      "description": "What happened and recommended action",
      "log_excerpt": "relevant log line(s)"
    }
  ],
  "summary": "Brief overall health summary"
}

If no issues warrant notification, return: {"issues": [], "summary": "No issues requiring attention."}
Do NOT report issues listed under the Ignore section in context. Do NOT report routine informational logs unless they indicate a problem."""

USER_TEMPLATE = """## User Context
{context}

## Log Entries (from {start} to {end})
{logs}

Analyze these logs and report only issues requiring attention."""


def _get_last_scan(path: str) -> datetime:
    p = Path(path)
    if p.exists():
        ts = p.read_text().strip()
        if ts:
            return datetime.fromisoformat(ts)
    return datetime.now(timezone.utc) - timedelta(hours=24)


def _set_last_scan(path: str, dt: datetime):
    Path(path).write_text(dt.isoformat())


def _read_recent_logs(log_dir: str, since: datetime) -> list[str]:
    entries = []
    log_path = Path(log_dir)
    if not log_path.exists():
        return entries
    for f in sorted(log_path.glob("*.jsonl")):
        try:
            stat = f.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            if mtime < since - timedelta(hours=1):
                continue
        except OSError:
            continue
        for line in f.read_text(errors="replace").splitlines():
            try:
                entry = json.loads(line)
                ts_str = entry.get("timestamp", "")
                if ts_str:
                    ts = datetime.fromisoformat(ts_str)
                    if ts.replace(tzinfo=timezone.utc) >= since:
                        entries.append(line)
                else:
                    entries.append(line)
            except (json.JSONDecodeError, ValueError):
                continue
    return entries


async def _analyze(cfg: Config) -> dict:
    last_scan = _get_last_scan(cfg.last_scan_file)
    now = datetime.now(timezone.utc)

    logs = _read_recent_logs(cfg.log_dir, last_scan)
    if not logs:
        _set_last_scan(cfg.last_scan_file, now)
        return {"issues": [], "summary": "No new log entries since last scan."}

    context_md = load_context(cfg.context_file)

    client = AsyncOpenAI(base_url=cfg.llm_base_url, api_key=cfg.llm_api_key)
    resp = await client.chat.completions.create(
        model=cfg.llm_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": USER_TEMPLATE.format(
                    context=context_md,
                    start=last_scan.isoformat(),
                    end=now.isoformat(),
                    logs="\n".join(logs[-2000:]),
                ),
            },
        ],
        response_format={"type": "json_object"},
    )

    _set_last_scan(cfg.last_scan_file, now)

    try:
        return json.loads(resp.choices[0].message.content)
    except json.JSONDecodeError:
        return {"issues": [], "summary": "Failed to parse LLM response."}


def _log_notif_history(path: str, issue: dict, sent: bool, timestamp: str):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    sev = issue.get("severity", "info")
    title = issue.get("title", "Issue detected")
    source = issue.get("source", "unknown")
    description = issue.get("description", "")
    log_excerpt = issue.get("log_excerpt", "")
    status = "SENT" if sent else "FILTERED"
    entry = (
        f"\n---\n\n"
        f"## [{sev.upper()}] {title} — {status}\n\n"
        f"- **Time:** {timestamp}\n"
        f"- **Source:** {source}\n"
        f"- **Status:** {status}\n\n"
        f"{description}\n\n"
        f"**Log:**\n```\n{log_excerpt}\n```\n"
    )
    with p.open("a", encoding="utf-8") as f:
        f.write(entry)


async def _notify_issues(cfg: Config, analysis: dict):
    sev_order = ["info", "low", "medium", "high", "urgent"]
    min_idx = sev_order.index(cfg.min_severity) if cfg.min_severity in sev_order else 0
    timestamp = datetime.now(timezone.utc).isoformat()
    for issue in analysis.get("issues", []):
        sev = issue.get("severity", "info")
        sev_idx = sev_order.index(sev) if sev in sev_order else 0
        if sev_idx < min_idx:
            _log_notif_history(cfg.notif_history_file, issue, sent=False, timestamp=timestamp)
            continue
        _log_notif_history(cfg.notif_history_file, issue, sent=True, timestamp=timestamp)
        priority = SEVERITY_PRIORITY.get(sev, 1)
        await send_gotify(
            cfg.gotify_url,
            cfg.gotify_token,
            title=f"[{sev.upper()}] {issue.get('title', 'Issue detected')}",
            message=(
                f"Source: {issue.get('source', 'unknown')}\n\n"
                f"{issue.get('description', '')}\n\n"
                f"Log:\n{issue.get('log_excerpt', '')}"
            ),
            priority=priority,
        )


async def run_scan(cfg: Config) -> dict:
    analysis = await _analyze(cfg)
    await _notify_issues(cfg, analysis)
    return analysis


@mcp.tool()
async def analyze_logs() -> str:
    """Manually trigger log analysis and return results."""
    cfg = Config.from_env()
    result = await run_scan(cfg)
    return json.dumps(result, indent=2)


@mcp.tool()
async def read_context() -> str:
    """Read the current context markdown file."""
    cfg = Config.from_env()
    return load_context(cfg.context_file)
