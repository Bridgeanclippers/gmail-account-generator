# Security Policy

## Scope

This tool automates account *creation flows* against Google's public
signup endpoints for research, QA, and load-testing of anti-abuse
systems. It does **not** ship with credentials, captcha-solving keys,
or proxy pools. You bring your own.

## Reporting

Email `security@gmail-account-generator.dev` (PGP key in
`.well-known/pgp.asc`). Do not open public issues for exploitable
findings.

## What we consider in scope

- Credential leakage through `config/` or logs.
- Proxy / SMS provider token leakage.
- Path traversal in the profile store.
- Anything that lets one run's data bleed into another.

## Out of scope

- Google-side rate limiting. That's the point of the tool.
- Your own OPSEC. Rotate your proxies.

## Hard rules for contributors

- Never commit `config/local.yaml`, `config/accounts.json`, or any
  `*.session`.
- Never log full cookies, tokens, or phone numbers. Hash them.
- SMS provider keys go in env, never in YAML.