# sslvpn_auto_test

Config-driven web automation framework for SSL VPN or similar web admin panels.

Built with Python + Playwright, this project can:

- Login to a web management UI automatically
- Navigate to target pages
- Fill string parameters
- Configure checkbox options
- Select dropdown options
- Be extended with custom action plugins

## 1. Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

## 2. Configure

Use `configs/example.yaml` as a template.

Main sections:

- `base_url`: Login page URL
- `browser`: Browser behavior (`headless`, `slow_mo`, `channel`)
- `credentials`: `username` and `password`
- `login`: CSS selectors for login form and success state
- `flows`: One or more automation flows
- `plugins`: Optional custom action plugins

Action fields:

- `type`: Action type
- `selector`: CSS selector (for most actions)
- `value`: Value to set (for `fill`, `select`, `set_checkbox`)

Built-in action types:

- `fill`
- `click`
- `check`
- `uncheck`
- `set_checkbox`
- `select`
- `wait`
- `press`
- `goto`

## 3. Run

Run all flows in config:

```bash
python main.py --config configs/example.yaml
```

Run one named flow:

```bash
python main.py --config configs/example.yaml --flow configure-sslvpn
```

## 4. Extend

Add a plugin file and register new action handlers via `register_actions(registry)`.

Example plugin is already included:

- `plugins/custom_actions.py`

Example custom action in YAML:

```yaml
- type: fill_if_empty
  selector: "#notes"
  value: "auto-filled once"
```

## 5. Notes

- Update all selectors in YAML to match your actual web page.
- For production usage, consider loading secrets from environment variables instead of writing passwords in plain text.
