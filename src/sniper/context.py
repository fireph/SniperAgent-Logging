from pathlib import Path


def load_context(path: str) -> str:
    p = Path(path)
    if p.exists():
        return p.read_text()
    return "# Sniper Context\n\n## Ignore\n\n## Notes\n"
