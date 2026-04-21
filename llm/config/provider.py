from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ProviderTypeConfig:
    """Static config for supported provider types in the settings UI."""

    name: str
    key: str
    icon: str
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


PROVIDER_TYPE_CONFIGS: list[ProviderTypeConfig] = [
    ProviderTypeConfig(
        name="OpenAI 兼容",
        key="openai",
        icon="https://www.svgrepo.com/show/306500/openai.svg",
    ),
]


def get_config_list() -> list[ProviderTypeConfig]:
    return list(PROVIDER_TYPE_CONFIGS)
