# Frontend Architecture

Status: Draft (Initial scaffold)  
Canonical Scope: Structure, layering, data flow, extension rules.

## 1. Layering Overview
| Layer | Purpose | Location | Depends On |
|-------|---------|----------|------------|
| Pages | Route-level composition & feature orchestration | `src/pages` | Components, Stores, Services, Router | 
| Components (UI / Domain) | Reusable visual + interaction units | `src/components` | Design tokens, Services (indirect), Stores |
| Stores (State) | Client-side domain state & caching | `src/stores` | Services |
| Services | API + blockchain integration, validation, orchestration | `src/services` | `boot/axios`, external SDKs |
| Token / Styling System | Theming & design tokens | `src/css`, `src/styles` | N/A |
| Boot Files | Global initialization (axios, pinia, assets, components) | `src/boot` | Config |

Principle: Pages never call the backend directly; they invoke store actions or services. Components should not instantiate services directly unless highly localized/isolated (e.g., a standalone Wallet connector widget). Prefer passing data & actions via props/emits.

## 2. Data Flow Summary
1. User Interaction → Component emits → Page handler → Store action → Service request → API / Wallet / Chain.
2. Services centralize error handling via `BaseService.handleRequest()`.
3. Fallback mock data patterns exist (`contributions`, `tokens`) → must be documented & eventually replaced with feature-flagged mock mode.

Sequence Example (Contribution Verification):
```
User clicks Verify → Page triggers store.verifyContribution(id,data)
  → store calls api.post('/contributions/{id}/verify')
    → on success: refetch contributions → UI re-renders updated list.
```

## 3. Core Conventions
- **Error Handling:** Use `BaseService` for network calls; UI surfaces meaningful errors via store `error` refs.
- **Loading States:** Each store maintains a `loading` ref (no global loader aggregator yet) — consider aggregation for multi-panel dashboards.
- **Resilience / Mocking:** If API fails, some stores seed example data. These fallbacks must be gated by an environment variable (`VITE_ENABLE_MOCKS` recommended) to avoid masking production issues.
- **Type Safety:** Public service/store interfaces must use exported TypeScript interfaces so consuming components avoid shape drift.

## 4. Services Overview (High-Level)
| Service | Responsibility | Notable Methods |
|---------|---------------|-----------------|
| `AIAgentService` | AI agent lifecycle, decisions, stats, training | `fetchAgents`, `fetchAgentDecisions`, `createAgent`, `overrideDecision` |
| `TokenService` | Cardano token balance, transfers (mint/burn placeholders) | `getTokenBalance`, `transferTokens` |
| `BondService` | (Planned) bond lifecycle logic | *TBD* |
| `CardanoService` | Wallet connection & address retrieval | `connectWallet` (via Mesh SDK) |
| `GovernanceService` | Governance proposals & voting (not yet audited) | *TBD* |
| `PerformanceMonitor` | Performance metrics capture | instrumentation hooks |

Full endpoint matrix is in `service-endpoint-matrix.md` (to be created).

## 5. State Stores Summary (Abbreviated)
| Store | Domain | Key State | Primary Actions |
|-------|--------|-----------|-----------------|
| `contributions` | Contributions | `contributions`, `loading` | `fetchContributions`, `createContribution`, `verifyContribution` |
| `tokens` | Token balances & tx | `balance`, `transactions` | `fetchBalance`, `transferTokens`, `stakeTokens` |
| `aiAgents` | AI agents & decisions | (Not yet inspected) | *TBD* |
| `cardanoWallet` | Wallet session | `isConnected`, `address` | `connect`, `disconnect` |
| `bonds` | Bond data | *TBD* | *TBD* |
| `governance` | Governance models | *TBD* | *TBD* |

A detailed catalog lives in `state-management.md` (to be created).

## 6. Routing Principles
- Flat page structure in `src/pages` → mapped via Quasar/Vue Router.
- Role-based dashboards (User / Contributor / Validator / Admin / Organization) should enforce guards (missing — add router guard spec in `routing-map.md`).
- Error page: `ErrorNotFound.vue` acts as 404 catch-all.

## 7. Theming & Tokens
- Canonical tokens: `design-system.md` (this file) + `FRONTEND_STYLING_GUIDE.md` for usage patterns.
- SCSS tokens (fluid) mirror CSS variables (static base). A mapping table prevents drift.

## 8. AI Agents Integration Surface
- Page: `AIAgentsDashboard.vue`
- Components: `AgentDecisionCard.vue`
- Services: composite pattern (`manager`, `decisions`, `training`, `stats`). Consolidation pattern encourages separation of concerns.

## 9. Technical Debt & Upcoming Refactors
| Area | Issue | Action |
|------|-------|--------|
| Mock fallback pattern | Silent substitution risks | Add feature flag + logging gate |
| TokenService mint/burn | Not implemented | Block UI until backend available; document roadmap |
| Role-based access | No documented guards | Implement route meta + global beforeEach |
| Store loading duplication | Repeated pattern | Abstract shared `useLoadingTracker` composable (future) |
| Service duplication risk | Some domain services TBD | Formalize service creation template |

## 10. Extension Guidelines
1. New feature → add service stub + store + page → update: architecture.md, routing-map.md, service-endpoint-matrix.md, state-management.md.
2. New design token → update: `quasar.variables.scss`, `design-tokens.scss`, `design-system.md`, mapping table.
3. Introduce API endpoint → reflect in service-endpoint matrix FIRST, then implement service method.

## 11. Open Questions
| Question | Owner | Needed By |
|----------|-------|-----------|
| Governance workflow (proposal lifecycle) | Product | Sprint N+1 |
| Bond analytics UI depth | Design | Prior to bond launch |
| Real-time performance streaming vs polling | Engineering | Perf milestone |

---
This scaffold will be expanded as other docs are added.
