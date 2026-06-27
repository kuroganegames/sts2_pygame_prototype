from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RunConfig:
    mode: str = "standard"
    seed: int | None = None
    custom: bool = False
    selected_modifiers: list[str] = field(default_factory=list)
    profile_eligible: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


def run_config_to_dict(config: RunConfig | dict | None) -> dict[str, Any]:
    if config is None:
        config = RunConfig()
    if isinstance(config, dict):
        base = run_config_to_dict(RunConfig())
        base.update(config)
        base["selected_modifiers"] = list(base.get("selected_modifiers", []) or [])
        base["metadata"] = dict(base.get("metadata", {}) or {})
        base["custom"] = bool(base.get("custom", False))
        base["profile_eligible"] = bool(base.get("profile_eligible", True))
        return base
    return {
        "mode": config.mode,
        "seed": config.seed,
        "custom": bool(config.custom),
        "selected_modifiers": list(config.selected_modifiers),
        "profile_eligible": bool(config.profile_eligible),
        "metadata": dict(config.metadata),
    }


def run_config_from_dict(data: dict | None) -> RunConfig:
    data = data or {}
    return RunConfig(
        mode=str(data.get("mode", "standard")),
        seed=data.get("seed"),
        custom=bool(data.get("custom", False)),
        selected_modifiers=list(data.get("selected_modifiers", []) or []),
        profile_eligible=bool(data.get("profile_eligible", True)),
        metadata=dict(data.get("metadata", {}) or {}),
    )
