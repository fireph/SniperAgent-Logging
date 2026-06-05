from dataclasses import dataclass
import os


@dataclass
class Config:
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = "syn:small:text"
    gotify_url: str = ""
    gotify_token: str = ""
    log_dir: str = "/data/logs"
    context_file: str = "/data/context.md"
    scan_interval_hours: int = 12
    last_scan_file: str = "/data/.last_scan"
    min_severity: str = "info"

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
            scan_interval_hours=int(os.getenv("SCAN_INTERVAL_HOURS", "12")),
            last_scan_file=os.getenv("LAST_SCAN_FILE", "/data/.last_scan"),
            min_severity=os.getenv("MIN_SEVERITY", "info").lower(),
        )
