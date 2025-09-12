# Frontend Environment Configuration

Canonical list of environment variables consumed by the frontend build/runtime. Update when adding or deprecating any variable. Variables are read via `import.meta.env` (Vite) and may require `VITE_` prefix to expose to client code.

## Variable Table
| Variable | Required | Default | Purpose | Notes |
|----------|----------|---------|---------|-------|
| VITE_API_BASE_URL | Yes | (none) | Base REST API origin (https://...) | Must not end with trailing slash |
| VITE_ENABLE_MOCKS | No | false | Force mock fallbacks even if API succeeds | Use only in local design review |
| VITE_LOG_LEVEL | No | info | Client log verbosity (debug, info, warn, error) | Wire into logger utility |
| VITE_FEATURE_BONDS | No | true | Toggle bonds module UI | Guard for staged rollout |
| VITE_FEATURE_AI_AGENTS | No | true | Toggle AI agents dashboard | Feature flag gating |
| VITE_FEATURE_GOVERNANCE | No | true | Toggle governance views |  |
| VITE_WALLET_NETWORK | No | testnet | Target Cardano network identifier | Align with backend chain config |
| VITE_NIMO_POLICY_ID | No | (placeholder) | Policy ID used to detect NIMO asset | Replace with production value |
| VITE_SENTRY_DSN | No | (none) | Error monitoring endpoint | Planned instrumentation |
| VITE_BUILD_SHA | CI | (none) | Injected commit SHA for diagnostics | Set in CI pipeline |
| VITE_BUILD_TIME | CI | (none) | ISO timestamp of build |  |
| VITE_APP_ENV | Yes | development | Environment label (development, staging, production) | Controls feature strictness |
| VITE_RATE_LIMIT_WARN | No | 500 | Threshold ms for warning on API call timing | Perf instrumentation |
| VITE_ANALYTICS_WRITE_KEY | No | (none) | Client analytics provider key | Do not set locally unless needed |

## Usage Pattern
Access only through a typed config wrapper (recommended future addition):
```ts
export const env = {
  apiBase: import.meta.env.VITE_API_BASE_URL,
  enableMocks: import.meta.env.VITE_ENABLE_MOCKS === 'true'
}
```

## Validation (Planned)
Add a startup validation module that:
1. Enumerates required variables.
2. Logs error & renders maintenance screen if missing in production.
3. Warns on unknown variables (typo detection).

## Local Development Setup
Copy `.env.template` → `.env` and fill required values:
```
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_ENV=development
VITE_WALLET_NETWORK=testnet
```

## Security Notes
- Never store secrets (private keys, API secrets) in Vite-exposed variables; all `VITE_` prefixed variables are bundled client-side.
- Use backend token exchange for sensitive operations.
- Avoid embedding analytics keys in forks without review.

## Change Control
- Removing a variable: deprecate (comment in template) for one sprint → remove from code → update table.
- Introducing variable: add row, update template, implement validation.

## TODOs
- Implement `env.ts` typed accessor with fallback warnings.
- Add Vitest tests for env validation logic once added.
- Sentry integration gating by `VITE_SENTRY_DSN`.

---
Last updated: 2025-09-07
Owner: Frontend Architecture Guild