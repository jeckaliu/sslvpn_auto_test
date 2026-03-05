from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from playwright.async_api import Page

from .config import Action

ActionHandler = Callable[[Page, Action], Awaitable[None]]


class ActionRegistry:
    def __init__(self) -> None:
        self._handlers: Dict[str, ActionHandler] = {}
        self._register_builtin_handlers()

    def register(self, action_type: str, handler: ActionHandler) -> None:
        self._handlers[action_type] = handler

    async def execute(self, page: Page, action: Action) -> None:
        handler = self._handlers.get(action.type)
        if handler is None:
            supported = ", ".join(sorted(self._handlers))
            raise ValueError(
                f"Unsupported action type '{action.type}'. Supported: {supported}"
            )
        await handler(page, action)

    def _register_builtin_handlers(self) -> None:
        self.register("fill", self._handle_fill)
        self.register("click", self._handle_click)
        self.register("check", self._handle_check)
        self.register("uncheck", self._handle_uncheck)
        self.register("set_checkbox", self._handle_set_checkbox)
        self.register("select", self._handle_select)
        self.register("wait", self._handle_wait)
        self.register("press", self._handle_press)
        self.register("goto", self._handle_goto)

    @staticmethod
    def _required_param(action: Action, key: str) -> Any:
        value = action.params.get(key)
        if value is None:
            raise ValueError(
                f"Action '{action.type}' requires parameter '{key}': {action.params}"
            )
        return value

    async def _handle_fill(self, page: Page, action: Action) -> None:
        selector = str(self._required_param(action, "selector"))
        value = str(self._required_param(action, "value"))
        await page.fill(selector, value)

    async def _handle_click(self, page: Page, action: Action) -> None:
        selector = str(self._required_param(action, "selector"))
        await page.click(selector)

    async def _handle_check(self, page: Page, action: Action) -> None:
        selector = str(self._required_param(action, "selector"))
        await page.check(selector)

    async def _handle_uncheck(self, page: Page, action: Action) -> None:
        selector = str(self._required_param(action, "selector"))
        await page.uncheck(selector)

    async def _handle_set_checkbox(self, page: Page, action: Action) -> None:
        selector = str(self._required_param(action, "selector"))
        value = bool(self._required_param(action, "value"))
        if value:
            await page.check(selector)
            return
        await page.uncheck(selector)

    async def _handle_select(self, page: Page, action: Action) -> None:
        selector = str(self._required_param(action, "selector"))
        value = self._required_param(action, "value")
        await page.select_option(selector, str(value))

    async def _handle_wait(self, page: Page, action: Action) -> None:
        if action.params.get("selector") is not None:
            selector = str(action.params["selector"])
            await page.wait_for_selector(selector)
            return

        ms = int(action.params.get("milliseconds", 1000))
        await page.wait_for_timeout(ms)

    async def _handle_press(self, page: Page, action: Action) -> None:
        selector = str(self._required_param(action, "selector"))
        key = str(self._required_param(action, "key"))
        await page.press(selector, key)

    async def _handle_goto(self, page: Page, action: Action) -> None:
        url = str(self._required_param(action, "url"))
        await page.goto(url, wait_until="networkidle")
