from dataclasses import dataclass
import os

from pytimeparse import parse as parse_duration


def _parse_duration(val: str, fallback: int) -> int:
    parsed = parse_duration(val)
    if parsed is not None:
        return int(parsed)
    if val.isdigit():
        return int(val)
    return fallback


@dataclass
class Config:
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = "syn:small:text"
    gotify_url: str = ""
    gotify_token: str = ""
    log_dir: str = "/data/logs"
    context_file: str = "/data/context.md"
    scan_interval: int = 21600
    last_scan_file: str = "/data/.last_scan"
    notif_history_file: str = "/data/notif_history.md"
    min_severity: str = "info"
    log_retention: int = 432000

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            llm_base_url=os.getenv("LLM_BASE_URL", "https://api.synthetic.new/openai/v1"),
            llm_api_key=os.getenv("LLM_API_KEY", ""),
            llm_model=os.getenv("LLM_MODEL", "syn:small:text"),
            gotify_url=os.getenv("GOTIFY_URL", ""),
            gotify_token=os.getenv("GOTIFY_TOKEN", ""),
            log_dir=os.getenv("LOG_DIR", "/data/logs"),
            context_file=os.getenv("CONTEXT_FILE", "/data/context.md"),
            scan_interval=_parse_duration(os.getenv("SCAN_INTERVAL", "6h"), 21600),
            last_scan_file=os.getenv("LAST_SCAN_FILE", "/data/.last_scan"),
            notif_history_file=os.getenv("NOTIF_HISTORY_FILE", "/data/notif_history.md"),
            min_severity=os.getenv("MIN_SEVERITY", "info").lower(),
            log_retention=_parse_duration(os.getenv("LOG_RETENTION", "5d"), 432000),
        )
