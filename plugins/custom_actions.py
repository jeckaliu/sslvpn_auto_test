from __future__ import annotations


def register_actions(registry) -> None:
    async def fill_if_empty(page, action):
        selector = str(action.params["selector"])
        value = str(action.params["value"])

        current = await page.input_value(selector)
        if not current:
            await page.fill(selector, value)

    registry.register("fill_if_empty", fill_if_empty)
