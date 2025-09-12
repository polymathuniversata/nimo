# Bonds Module (Impact Investment)

Canonical reference for frontend implementation of impact bonds: data flow, services, store contract, UI surfaces, extensibility.

## Purpose
Provide a marketplace for funding socially impactful projects (education, environment, empowerment, etc.) while tracking funding progress, investments, returns, and regional/category analytics.

## Architecture Overview
| Layer | Role | Files |
|-------|------|------|
| Store | Reactive state & orchestration | `stores/bonds.ts` |
| Service Facade | Unified API surface (delegates internally) | `services/bond/bond-service.ts` (`BondService`) |
| Operations Service | Mutating operations (create, invest) | `BondOperationsService` |
| Data Service | Fetch lists & stats | `BondDataService` |
| Base Service | Shared logic (validation, calculations) | `BaseBondService` |

Facade pattern isolates UI from internal service refactors.

## Data Models (Frontend)
| Entity | Key Fields | Notes |
|--------|-----------|------|
| ImpactBond | id, title, category, targetFunding, currentFunding, duration, expectedImpact, milestones[], status, endDate, userInvestment? | Funding progress & expected return derived |
| BondInvestment | id, bondId, amount, investor, date, returns?, status | `returns` optional until matured |
| BondStats | activeBonds, totalInvested, avgReturn, successfulProjects | High-level KPI |
| CategoryStats | name, count, investment | Category distribution |
| RegionStats | name, investment, projects | Regional distribution |

## Store (`bonds`)
State: `activeBonds`, `myInvestments`, `stats`, `categoryStats`, `regionStats`, `loading`, `investmentsLoading`.
Actions ↔ Service Mapping:
| Store Action | Service Call | Endpoint | Fallback |
|--------------|-------------|----------|----------|
| fetchActiveBonds | `bondService.fetchActiveBonds` | GET /bonds/active | Mock list |
| fetchMyInvestments | `bondService.fetchMyInvestments` | GET /bonds/my-investments | Mock list |
| fetchStats | `bondService.fetchStats` | GET /bonds/stats | Mock stats |
| createBond | `bondService.createBond` | POST /bonds | Local synthetic bond on fail |
| investInBond | `bondService.investInBond` | POST /bonds/{id}/invest | Local funding + investment add |
| getBondById | `bondService.getBondById` | GET /bonds/{id} | N/A |
| getBondsByCategory | `bondService.getBondsByCategory` | GET /bonds?category= | N/A |
| getBondsByLocation | `bondService.getBondsByLocation` | GET /bonds?location= | N/A |
| getInvestmentById | `bondService.getInvestmentById` | GET /bonds/investments/{id} | N/A |
| calculateExpectedReturn | `bondService.calculateExpectedReturn` | (local calc) | Deterministic |

## Derived Calculations
- Expected Return: Weighted by category multiplier & duration factor (see BaseBondService). Example: 12‑month Education project ~ base 8% * 1.2 * 1 = 9.6%.
- Funding Progress: `(currentFunding / targetFunding) * 100` (capped 100%).
- Color Coding: progress >=100 positive, >=75 warning, else negative.

## User Flows
### Create Bond
1. User opens create form (title, category, target funding, duration months, expected impact, milestones newline separated).
2. Store `createBond` -> POST /bonds.
3. On success: refresh active bonds (optional optimization: prepend without refetch).
4. On failure: local synthetic bond inserted with generated id (mock path) for continued UI iteration.

### Invest in Bond
1. User inputs amount & submits.
2. Store action validates via backend (service fetches bond first) then POST /bonds/{id}/invest.
3. Refresh: `fetchMyInvestments` + `fetchActiveBonds` to update funding progress.
4. Fallback: mutate funding & add synthetic investment.

### View Analytics
- `fetchStats` loads stats, categories, regions. Mock path supplies consistent sample for layout.

## UI Surfaces (Planned / Existing)
| Surface | Purpose | Notes |
|---------|---------|------|
| Bond List / Marketplace | Explore active bonds | Grid or table with filter chips (category, region) |
| Bond Detail Drawer/Page | Deep dive: milestones, funding progress, expected return | Includes invest form if active |
| My Investments | Portfolio view, returns tracking | Table grouped by status |
| Analytics Dashboard | Category & region distribution, KPIs | Charts (donut/bar) |

## Validation & Constraints
- Minimum investment = 1 ADA (constant in BaseBondService.MINIMUM_INVESTMENT).
- `validateInvestmentAmount` ensures amount <= remaining target.
- Milestones parsed by splitting newline string; empty trimmed out.

## Fallback Strategy
- Read operations fallback to deterministic mock arrays (enables skeleton UI dev).
- Mutations fallback to local synthetic success, ensuring user feedback loop.
- Fallbacks MUST NOT persist beyond development; production flag / build guard recommended (TODO).

## Extensibility Roadmap
| Feature | Approach |
|---------|----------|
| Secondary Market (selling stakes) | New endpoint `/bonds/investments/{id}/list` + store action |
| Returns Projection Chart | Extend `calculateExpectedReturn` to include time curve |
| Bond Maturity Events | Scheduler pushes status changes; UI polls or subscribes |
| Region Drilldown | Dedicated route with map visualization |
| Staking / Locking Mechanism | Additional service layer pre-invest validation |

## Monitoring & Metrics (Planned)
- Track creation success/fail counts.
- Investment attempt latency & failure reasons.
- Funding velocity (delta funding/time) calculated client side initially.

## Security Considerations
- Input validation enforced both client (length, numeric) and server side.
- Role gating for bond creation (backend). UI hides create CTA if unauthorized.
- Prevent over-investment race (server authoritative; client optimistic only after confirm).

## Test Coverage Suggestions
- `validateInvestmentAmount` boundary tests (0, min-1, remaining+1).
- Mock fallback injection when network error thrown.
- Progress color classification thresholds.
- Synthetic bond creation path structure integrity.

## TODO Summary
- Production flag to disable mock mutations.
- Real-time funding updates (WebSocket or polling diff merge).
- Responsive layout stress test for >50 active bonds.

---
Last updated: 2025-09-07
Owner: Frontend Architecture Guild