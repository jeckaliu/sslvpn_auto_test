from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class BrowserConfig:
    headless: bool = True
    slow_mo: int = 0
    channel: Optional[str] = None


@dataclass
class Credentials:
    username: str
    password: str


@dataclass
class LoginConfig:
    username_selector: str
    password_selector: str
    submit_selector: str
    success_selector: Optional[str] = None


@dataclass
class Action:
    type: str
    params: Dict[str, Any] = field(default_factory=dict)

    @property
    def selector(self) -> Optional[str]:
        selector = self.params.get("selector")
        return str(selector) if selector is not None else None

    @property
    def value(self) -> Any:
        return self.params.get("value")


@dataclass
class Flow:
    name: str
    url: Optional[str]
    actions: List[Action]


@dataclass
class AutomationConfig:
    base_url: str
    browser: BrowserConfig
    credentials: Credentials
    login: LoginConfig
    flows: List[Flow]
    plugins: List[str] = field(default_factory=list)


def _require(raw: Dict[str, Any], key: str) -> Any:
    if key not in raw:
        raise ValueError(f"Missing required config key: '{key}'")
    return raw[key]


def _parse_action(raw: Dict[str, Any]) -> Action:
    if not isinstance(raw, dict):
        raise ValueError(f"Action must be a map, got: {type(raw)!r}")
    action_type = _require(raw, "type")
    params = {k: v for k, v in raw.items() if k != "type"}
    return Action(type=str(action_type), params=params)


def _parse_flow(raw: Dict[str, Any]) -> Flow:
    if not isinstance(raw, dict):
        raise ValueError(f"Flow must be a map, got: {type(raw)!r}")
    name = str(_require(raw, "name"))
    raw_actions = _require(raw, "actions")
    if not isinstance(raw_actions, list):
        raise ValueError(f"Flow actions must be a list in flow '{name}'")
    actions = [_parse_action(item) for item in raw_actions]
    return Flow(name=name, url=raw.get("url"), actions=actions)


def load_config(config_path: str | Path) -> AutomationConfig:
    config_file = Path(config_path)
    with config_file.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    if not isinstance(raw, dict):
        raise ValueError("Top-level config must be a map")

    browser_raw = raw.get("browser", {})
    if not isinstance(browser_raw, dict):
        raise ValueError("'browser' must be a map")

    credentials_raw = _require(raw, "credentials")
    login_raw = _require(raw, "login")
    flows_raw = _require(raw, "flows")

    if not isinstance(credentials_raw, dict):
        raise ValueError("'credentials' must be a map")
    if not isinstance(login_raw, dict):
        raise ValueError("'login' must be a map")
    if not isinstance(flows_raw, list):
        raise ValueError("'flows' must be a list")

    browser = BrowserConfig(
        headless=bool(browser_raw.get("headless", True)),
        slow_mo=int(browser_raw.get("slow_mo", 0)),
        channel=browser_raw.get("channel"),
    )

    credentials = Credentials(
        username=str(_require(credentials_raw, "username")),
        password=str(_require(credentials_raw, "password")),
    )

    login = LoginConfig(
        username_selector=str(_require(login_raw, "username_selector")),
        password_selector=str(_require(login_raw, "password_selector")),
        submit_selector=str(_require(login_raw, "submit_selector")),
        success_selector=(
            str(login_raw["success_selector"])
            if login_raw.get("success_selector") is not None
            else None
        ),
    )

    flows = [_parse_flow(item) for item in flows_raw]
    plugins = raw.get("plugins", [])
    if not isinstance(plugins, list):
        raise ValueError("'plugins' must be a list if provided")

    return AutomationConfig(
        base_url=str(_require(raw, "base_url")),
        browser=browser,
        credentials=credentials,
        login=login,
        flows=flows,
        plugins=[str(item) for item in plugins],
    )
