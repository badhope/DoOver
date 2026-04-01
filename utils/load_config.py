import json
from pathlib import Path
from typing import Any

def load_json_config(config_path: str | Path) -> dict[str, Any]:
    with Path(config_path).open("r", encoding="utf-8") as f:
        return json.load(f)
