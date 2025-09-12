# Frontend State Management

Canonical documentation for how client state is organized, the contract each Pinia store exposes, and interaction patterns between stores, services, and UI layers. This doc is authoritative: code MUST either follow it or extend it (in which case update this file in the same PR).

## Principles

1. Single Responsibility – each store owns one cohesive domain (auth, tokens, contributions, governance, bonds, AI agents, wallet). Avoid "misc" stores.
2. Explicit Side‑Effects – All network / service calls happen inside store actions (or services invoked by those actions). Components never call raw `api.*` except in truly local ephemeral flows.
3. Mock Friendly – When backend capability is missing, stores fall back to deterministic mock scaffolds (documented below) without changing API surface.
4. Progressive Enhancement – Real data replaces mock seamlessly once endpoints exist.
5. Idempotent Fetch – Repeated fetches should not corrupt state; actions either fully succeed or surface error.
6. View Derivation – Components derive everything from state + getters; no duplicated derivations at component level.

## Store Inventory Overview

| Store | File | Domain | Core State | Key Actions | Mock Fallbacks |
|-------|------|--------|------------|-------------|----------------|
| Auth | `stores/auth.ts` | Session & RBAC | `user`, `isAuthenticated`, `loading`, `error` | `login`, `register`, `registerWithWallet`, `logout`, `updateUser` | N/A (no mock user inserted automatically) |
| Tokens | `stores/tokens.ts` | Token balance & economic actions | `balance`, `transactions`, `loading`, `error` | `fetchBalance`, `fetchTransactions`, `transferTokens`, `stakeTokens` | Random balance + hardcoded sample transactions on failure |
| Contributions | `stores/contributions.ts` | User & global contribution catalog | `contributions`, `loading`, `error` | `fetchContributions`, `createContribution`, `verifyContribution`, `getContributionExplanation` | Two illustrative contributions with verification data |
| AI Agents | `stores/aiAgents.ts` | Autonomous agents registry & decisions | `agents`, `recentDecisions`, `stats`, `loading`, `decisionsLoading` | `fetchAgents`, `fetchRecentDecisions`, `fetchStats`, `createAgent`, `overrideDecision` | 3 agent archetypes + 3 recent decisions + stats |
| Bonds | `stores/bonds.ts` | Impact bonds marketplace & investments | `activeBonds`, `myInvestments`, `stats`, `categoryStats`, `regionStats`, `loading`, `investmentsLoading` | `fetchActiveBonds`, `fetchMyInvestments`, `fetchStats`, `createBond`, `investInBond` | 3 sample bonds + investments + computed stats |
| Governance | `stores/governance.ts` | Proposals, voting, governance params | `activeProposals`, `proposalHistory`, `stats`, `governanceParams`, `userStats`, `loading`, `historyLoading` | `fetchActiveProposals`, `fetchProposalHistory`, `fetchStats`, `fetchUserStats`, `fetchGovernanceParams`, `createProposal`, `voteOnProposal` | 3 active + 2 historical proposals + stats |
| Cardano Wallet | `stores/cardanoWallet.ts` | Real wallet connection orchestration | `wallet`, `connectedWallet`, `transactions`, `isConnecting`, `isLoading`, `error`, `availableWallets`, `lastRefresh` | `connectWallet`, `disconnectWallet`, `loadWalletInfo`, `loadTransactions`, `sendTransaction`, `sendToken`, `refreshWallet`, `checkConnection`, `initialize` | Silent: UI relies on absence of connection; no random fabrication |
| Simple Wallet (legacy/demo) | `stores/wallet.ts` & `stores/wallet-simple.ts` | Transitional / demo-only wallet abstraction | `isConnected`, `address`, `balance`, etc. | `connectWallet`, `disconnectWallet`, `refreshBalance` | Random balance generation |

> Action: Legacy simple wallet stores should be deprecated once `cardanoWallet` store is fully adopted. Track removal in a deprecation schedule.

## Cross-Cutting Conventions

- All stores created via `defineStore` using the Composition API form for tree‑shakability.
- `loading` flags are per-store; long-running secondary actions use distinct flags (`decisionsLoading`, `historyLoading`, etc.).
- Errors are string (user-displayable) or null; raw exceptions are logged to console only.
- Side effects (notifications) use Quasar `Notify` inside store actions only for user-triggered pathways (connect, override, refresh). Fetching lists silently fails to console + mock fallback.
- Mock fallback pattern: catch network error -> log -> inject deterministic sample -> (optional) user notification of mock usage (AI agents store does this).

## Detailed Store Contracts

### Auth Store (`auth`)
State: `user: User|null`, `isAuthenticated: boolean`, `loading: boolean`, `error: string|null`.
Derived: Role helpers (`hasRole`, `hasPermission`, `hasAnyRole`, `getUserRoles`, `getPrimaryRole`, `getPreferredDashboard`).
Actions:
- `login(LoginData)` – POST `/auth/login`, persists tokens through `secureTokenService` (access+refresh) and sets `isAuthenticated`.
- `register(RegisterData)` – POST `/auth/register` (no auto-login).
- `registerWithWallet(WalletRegistrationData)` – POST `/auth/register/wallet`, then authenticates session.
- `logout()` – Clears user & token state + legacy localStorage cleanup.
Resilience: No mock user provided; failures surface error.
Security: Tokens stored via `secureTokenService` only; DO NOT access localStorage directly in components.

### Tokens Store (`tokens`)
State: `balance: number`, `transactions: TokenTransaction[]`, `loading`, `error`.
Actions:
- `fetchBalance()` – GET `/tokens/balance`; on failure sets random plausible balance (documented dev-only behavior; remove for prod).
- `fetchTransactions()` – Currently supplies mock array (replace with GET `/tokens/transactions`).
- `transferTokens(TransferData)` – POST `/tokens/transfer` then refreshes balance + transactions.
- `stakeTokens(StakeData)` – POST `/tokens/stake` then refreshes balance.
Consistency: Always await refresh operations so UI shows settled state.

### Contributions Store (`contributions`)
State: `contributions: Contribution[]`, `loading`, `error`.
Actions:
- `fetchContributions(params)` – GET `/contributions` with query params; fallback injects two sample contributions.
- `createContribution(data)` – POST `/contributions/`; optimistic prepend on success only.
- `verifyContribution(id, verificationData)` – POST `/contributions/{id}/verify` then refetch list.
- `getContributionExplanation(id)` – GET `/contributions/{id}/explain`.
Pagination: Future: maintain `pagination` object (page, perPage, total) – TODO.

### AI Agents Store (`aiAgents`)
State: `agents: AIAgent[]`, `recentDecisions: AgentDecision[]`, `stats: AgentStats`, `loading`, `decisionsLoading`.
Actions: `fetchAgents`, `fetchRecentDecisions`, `fetchStats`, `createAgent`, `overrideDecision`.
Fallback: Inserts 3 archetypal agents & decisions; notifies user once (`Using mock agent data`).
Extensibility: Add action `streamAgentEvents()` (SSE/WebSocket) – TODO.

### Bonds Store (`bonds`)
State: `activeBonds`, `myInvestments`, `stats`, `categoryStats`, `regionStats`, `loading`, `investmentsLoading`.
Actions: `fetchActiveBonds`, `fetchMyInvestments`, `fetchStats`, `createBond`, `investInBond`.
Fallback: 3 bonds + sample investments; computed stats used when API fails.
Roadmap: Separate `analytics` sub-module if metrics grow – TODO.

### Governance Store (`governance`)
State: `activeProposals`, `proposalHistory`, `stats`, `governanceParams`, `userStats`, `loading`, `historyLoading`.
Actions: `fetchActiveProposals`, `fetchProposalHistory`, `fetchStats`, `fetchUserStats`, `fetchGovernanceParams`, `createProposal`, `voteOnProposal`.
Fallback: Predefined active + historical proposals with vote tallies.
Enhancements: Add optimistic vote update w/ rollback – TODO.

### Cardano Wallet Store (`cardanoWallet`)
State: `wallet`, `connectedWallet`, `transactions`, `isConnecting`, `isLoading`, `error`, `availableWallets`, `lastRefresh`.
Getters: `isConnected`, `balance`, `adaBalance`, `address`, `network`, `stakeAddress`, `walletName`, `canRefresh`, `recentTransactions`, `pendingTransactions`.
Actions: Connectivity (`connectWallet`, `disconnectWallet`, `initialize`), Data (`loadWalletInfo`, `loadTransactions`, `refreshWallet`, `checkConnection`), Transactions (`sendTransaction`, `sendToken`), Utilities (`validateAddress`, `formatADA`, `getWalletInstallUrl`, `getSupportedWallets`, `clearError`).
Frequencies: `refreshWallet` guard ensures ≥30s between refresh attempts (`canRefresh`).
Dual Source: Combines browser wallet adapter + backend sync; failures of backend do not abort UI connectivity.

### Simple / Legacy Wallet Stores (`wallet`, `wallet-simple`)
Purpose: Developer demo & transitional abstraction before full Cardano integration.
Action: Plan deprecation; mark any new component usage as tech debt.
Deprecation Steps:
1. Replace imports of `useWalletStore` with `useCardanoWalletStore` where feasible.
2. Migrate UI computed logic to new getters.
3. Remove files after 0 consumers (tracked via grep) – create removal issue.

## Interaction Patterns

| Scenario | Flow | Notes |
|----------|------|-------|
| Authenticated token transfer | UI -> `tokens.transferTokens` -> POST -> refresh balance+transactions -> UI updates via refs | Errors surfaced via `error` + thrown for form handling |
| Contribution creation | UI -> `contributions.createContribution` -> POST -> prepend -> optional success notify | No optimistic mutation before server ack |
| AI agent creation | UI -> `aiAgents.createAgent` -> service -> refresh list -> UI | Mock path still adds local agent |
| Bond investment | UI -> `bonds.investInBond` -> service -> refresh investments & active bonds | Maintains userInvestment aggregate |
| Governance vote | UI -> `governance.voteOnProposal` -> service -> refresh active proposals | TODO: optimistic path |
| Wallet connect | UI -> `cardanoWallet.connectWallet` -> wallet adapter -> (backend sync) -> load tx -> UI | Fallback still allows basic display |

## Error Handling Contract

- All store actions throw on unrecoverable failures (e.g., form submissions), while still setting `error` for reactive display.
- Fetch/list actions that can mock do NOT throw; they set `error` + fill mock data.
- Components must not rely solely on thrown exceptions; always watch store `error`.

## Testing Guidance (Preview)
A dedicated `testing-strategy.md` will enumerate coverage goals. Minimum per store:
- Happy path for each public action (mock service resolved).
- Failure path triggers mock fallback (where defined).
- Getter derivations (e.g., `preferredDashboard`, `canRefresh`).
- Deprecation: ensure no new tests imported from legacy wallet after migration.

## Roadmap / TODO Summary (Tracked)
- Pagination object in contributions store.
- SSE/WebSocket streaming for AI decisions.
- Governance optimistic vote with rollback.
- Bonds analytics module extraction.
- Deprecate legacy wallet stores.

## Maintenance Checklist
- When adding a new store: update table, describe fallback policy, define actions & side‑effects, add tests, link from `architecture.md`.
- When altering a store contract (rename/remove action): bump minor version in CHANGELOG (to introduce), update dependent docs, migrate components.

---
Last updated: 2025-09-07
Owner: Frontend Architecture Guild