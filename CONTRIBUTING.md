# Contributing to gmail-account-generator

This is an open hobbyist automation research repo. PRs welcome.

## Ground rules

- Python 3.11+. Target is Windows 10/11 x64, but the core must stay
  platform-agnostic; Windows-specific bits live under `adapters/windows/`.
- No hardcoded credentials. Everything through `config/settings.py` +
  env vars.
- Every new `services/` module gets a matching test under `tests/`.
- Handlers stay thin. If a handler is doing business logic, it belongs
  in `services/`.
- Type hints required on public functions. `mypy --strict` on `core/`,
  `services/`, `models/`.

## Layout

```
gmail_account_generator/
  bootstrap/     entry + DI wiring
  handlers/      thin orchestration per workflow
  services/      business logic
  adapters/      platform + external IO (windows, http, sms, captcha)
  models/        dataclasses, schemas
  utils/         pure helpers, no IO
  config/        settings + presets
```

## Running tests

```bash
python -m pytest -q
```

## Style

`ruff format` + `ruff check`. Line length 100.