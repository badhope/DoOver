import json
from pathlib import Path
from typing import Any


def load_json_config(config_path: str | Path) -> dict[str, Any]:
    with Path(config_path).open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json_config(config_path: str | Path, data: dict[str, Any]) -> None:
    path = Path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
