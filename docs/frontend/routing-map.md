# Routing Map

Status: Draft  
Canonical Source for page-level intent, roles, and navigation hierarchy.

## 1. Route Inventory
| File | Proposed Route Path | Purpose | Role / Access | Notes |
|------|---------------------|---------|---------------|-------|
| `IndexPage.vue` | `/` | Landing / dashboard entry (contextual redirect) | Public (redirects if authed) | Add logic: if authed → /dashboard |
| `UserDashboard.vue` | `/dashboard` | General user overview | Authenticated | Could merge with Contributor if roles unify |
| `ContributorDashboard.vue` | `/dashboard/contributor` | Contribution stats & actions | Contributor | Role meta: `roles: ['contributor']` |
| `ValidatorDashboard.vue` | `/dashboard/validator` | Validation queue & metrics | Validator | Role meta |
| `AdminDashboard.vue` | `/dashboard/admin` | Platform oversight & metrics | Admin | Guard pending |
| `AIAgentsDashboard.vue` | `/ai/agents` | Monitor & manage AI agents | Admin / Analyst | Requires decision override permissions |
| `ContributionsPage.vue` | `/contributions` | List & filter contributions | Authenticated | Pagination + filters |
| `ContributionDetailPage.vue` | `/contributions/:id` | View single contribution | Authenticated | Prefetch by id |
| `CreateContributionPage.vue` | `/contributions/create` | Submit new contribution | Contributor | Guard for verified email? |
| `TokensPage.vue` | `/tokens` | Token balance & transfers | Authenticated (wallet linked) | Show link wallet CTA if not connected |
| `CardanoWalletPage.vue` | `/wallet` | Full wallet management | Authenticated | Cardano-specific actions |
| `CardanoWalletPageSimple.vue` | `/wallet/simple` | Simplified wallet connect | Authenticated | Onboarding step |
| `GovernancePage.vue` | `/governance` | Proposals & voting | Authenticated | Future: role-based voting weight |
| `ImpactBondsPage.vue` | `/bonds` | Impact bond exploration | Authenticated | Bond metrics pending |
| `OrganizationDashboard.vue` | `/org/:slug/dashboard` | Org-level overview | Org Admin / Member | Slug param |
| `OrganizationProjects.vue` | `/org/:slug/projects` | Org projects list | Org Member | Add create project guard |
| `OrganizationContributors.vue` | `/org/:slug/contributors` | Members & roles | Org Admin | Role editing UI |
| `OrganizationAnalytics.vue` | `/org/:slug/analytics` | Impact & performance analytics | Org Admin | Heavy queries: lazy load |
| `OrganizationSettings.vue` | `/org/:slug/settings` | Org configuration | Org Admin | Sensitive actions audit |
| `ProfilePage.vue` | `/profile` | User profile & identity | Authenticated | Add DID integration placeholder |
| `WalletConnect.vue` | `/wallet/connect` | Legacy/alternate connect screen | Authenticated | Consider merge into /wallet |
| `HeaderTest.vue` | `/dev/header-test` | Dev / design review sandbox | Dev-only | Guard by env flag |
| `ErrorNotFound.vue` | `/:catchAll(.*)*` | 404 page | Public | Always last |

## 2. Guard & Meta Policy
Add a central route meta schema:
```ts
interface RouteMeta {
  auth?: boolean;
  roles?: string[]; // e.g. ['admin','contributor']
  orgContext?: boolean; // requires active org selection
  wallet?: boolean; // requires connected wallet
  featureFlag?: string; // e.g. 'impactBonds'
}
```

## 3. Recommended Router Enhancements
1. Global `beforeEach`:
   - If `meta.auth` and no session → redirect `/` with `?redirect=` param.
   - If `meta.roles` mismatch → redirect `/dashboard` (or 403 page if added).
   - If `meta.wallet` and wallet not connected → redirect `/wallet`.
   - If `meta.featureFlag` not enabled → redirect fallback or show controlled 404.
2. Add progress indicator (optional) using `LoadingBar` plugin between large page transitions.
3. Prefetch strategy: lightweight prefetch of critical store queries on certain dashboards.

## 4. Navigation Hierarchy (Primary)
```
Dashboard
 ├─ Contributions
 │   ├─ List (/contributions)
 │   ├─ Detail (/contributions/:id)
 │   └─ Create (/contributions/create)
 ├─ Tokens (/tokens)
 ├─ AI Agents (/ai/agents) [admin]
 ├─ Governance (/governance)
 ├─ Impact Bonds (/bonds)
 └─ Organization (/org/:slug/...)
```

## 5. Open Items
| Area | Question | Decision Needed By |
|------|----------|--------------------|
| Governance route naming | Should proposals be nested? | Before governance feature freeze |
| Wallet flow duplication | Consolidate `/wallet` vs `/wallet/connect`? | After UX review |
| DID integration | Add `/identity` route? | After backend DID MVP |
| Dev pages | Hide or namespace dev utilities? | Prior to public beta |

## 6. Implementation TODO (Post-Doc)
- [ ] Implement route meta typing & global guard.
- [ ] Create feature flag helper (`useFeatureFlag`).
- [ ] Add 403 or soft-denied component.
- [ ] Remove / refactor `HeaderTest.vue` before production.

---
This document is authoritative for routing changes. Update here BEFORE modifying router configuration.
