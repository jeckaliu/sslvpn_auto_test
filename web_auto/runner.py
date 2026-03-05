from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

from playwright.async_api import Page, async_playwright

from .actions import ActionRegistry
from .config import AutomationConfig, Flow


class WebAutomationRunner:
    def __init__(self, config: AutomationConfig, config_path: str | Path) -> None:
        self.config = config
        self.config_dir = Path(config_path).resolve().parent
        self.registry = ActionRegistry()

    def load_plugins(self) -> None:
        for plugin_path in self.config.plugins:
            self._load_plugin(plugin_path)

    def _load_plugin(self, plugin_path: str) -> None:
        path = Path(plugin_path)
        if not path.is_absolute():
            path = self.config_dir / path
        path = path.resolve()

        if not path.exists():
            raise FileNotFoundError(f"Plugin file not found: {path}")

        module_name = f"web_auto_plugin_{path.stem}_{abs(hash(str(path)))}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load plugin from {path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        register_fn = getattr(module, "register_actions", None)
        if not callable(register_fn):
            raise ValueError(
                f"Plugin '{path}' must expose register_actions(registry) function"
            )
        register_fn(self.registry)

    async def run(self, flow_name: Optional[str] = None) -> None:
        self.load_plugins()

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.config.browser.headless,
                slow_mo=self.config.browser.slow_mo,
                channel=self.config.browser.channel,
            )
            context = await browser.new_context()
            page = await context.new_page()

            await self._login(page)

            selected_flows = self._pick_flows(flow_name)
            for flow in selected_flows:
                await self._run_flow(page, flow)

            await context.close()
            await browser.close()

    def _pick_flows(self, flow_name: Optional[str]) -> list[Flow]:
        if flow_name is None:
            return self.config.flows

        for flow in self.config.flows:
            if flow.name == flow_name:
                return [flow]

        available = ", ".join(item.name for item in self.config.flows)
        raise ValueError(f"Flow '{flow_name}' not found. Available flows: {available}")

    async def _login(self, page: Page) -> None:
        await page.goto(self.config.base_url, wait_until="networkidle")
        await page.fill(
            self.config.login.username_selector,
            self.config.credentials.username,
        )
        await page.fill(
            self.config.login.password_selector,
            self.config.credentials.password,
        )
        await page.click(self.config.login.submit_selector)

        if self.config.login.success_selector:
            await page.wait_for_selector(self.config.login.success_selector)
        else:
            await page.wait_for_load_state("networkidle")

    async def _run_flow(self, page: Page, flow: Flow) -> None:
        if flow.url:
            target_url = urljoin(self.config.base_url.rstrip("/") + "/", flow.url)
            await page.goto(target_url, wait_until="networkidle")

        for action in flow.actions:
            await self.registry.execute(page, action)
