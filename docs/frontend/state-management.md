# Frontend State Management

Canonical documentation for how client state is organized, the contract each React Context exposes, and interaction patterns between contexts, services, and UI layers. This doc is authoritative: code MUST either follow it or extend it (in which case update this file in the same PR).

## Architecture Overview

**Nimo Frontend uses React Context API instead of Pinia stores** for state management. This decision was made because:

1. **React Native**: The project is built with React (not Vue), so React Context is the natural choice
2. **Consistency**: All components use React patterns throughout
3. **Flexibility**: React Context provides the same functionality as stores with better React integration
4. **Performance**: Context provides efficient state sharing without external dependencies

## Principles

1. Single Responsibility – each context owns one cohesive domain (auth, tokens, contributions, governance, bonds, AI agents, wallet). Avoid "misc" contexts.
2. Explicit Side‑Effects – All network / service calls happen inside context actions (or services invoked by those actions). Components never call raw `api.*` except in truly local ephemeral flows.
3. Mock Friendly – When backend capability is missing, contexts fall back to deterministic mock scaffolds (documented below) without changing API surface.
4. Progressive Enhancement – Real data replaces mock seamlessly once endpoints exist.
5. Idempotent Fetch – Repeated fetches should not corrupt state; actions either fully succeed or surface error.
6. View Derivation – Components derive everything from state + getters; no duplicated derivations at component level.

> **⚠️ IMPORTANT UPDATE: September 20, 2025**
>
> This project uses **React Context API** instead of Pinia stores as originally documented.
> - **AuthContext** (✅ Complete) - `contexts/AuthContext.tsx`
> - **TokenContext** (✅ Complete) - `contexts/TokenContext.tsx`
> - **ContributionsContext** (✅ Complete) - `contexts/ContributionsContext.tsx`
> - **WalletContext** (✅ Complete) - `contexts/WalletContext.tsx`
>
> All contexts are fully implemented with useReducer for complex state management, providing equivalent functionality to stores but with native React patterns.

## Context Inventory Overview

| Context | File | Domain | Core State | Key Actions | Mock Fallbacks |
|---------|------|--------|------------|-------------|----------------|
| Auth | `contexts/AuthContext.tsx` | Session & RBAC | `user`, `isAuthenticated`, `loading`, `error` | `login`, `register`, `registerWithWallet`, `logout`, `updateUser` | N/A (no mock user inserted automatically) |
| Tokens | `contexts/TokenContext.tsx` | Token balance & economic actions | `balance`, `transactions`, `loading`, `error` | `fetchBalance`, `fetchTransactions`, `transferTokens`, `stakeTokens` | Random balance + hardcoded sample transactions on failure |
| Contributions | `contexts/ContributionsContext.tsx` | User & global contribution catalog | `contributions`, `loading`, `error` | `fetchContributions`, `createContribution`, `verifyContribution`, `getContributionExplanation` | Two illustrative contributions with verification data |
| Wallet | `contexts/WalletContext.tsx` | Cardano wallet connection orchestration | `wallet`, `connectedWallet`, `transactions`, `isConnecting`, `isLoading`, `error` | `connectWallet`, `disconnectWallet`, `loadWalletInfo`, `loadTransactions`, `sendTransaction`, `sendToken`, `refreshWallet`, `checkConnection`, `initialize` | Silent: UI relies on absence of connection; no random fabrication |

## Implementation Details

All contexts are implemented using React's `useReducer` hook for complex state management, providing the same benefits as Pinia stores but with native React patterns.

> Action: Legacy simple wallet stores should be deprecated once `cardanoWallet` store is fully adopted. Track removal in a deprecation schedule.

## Cross-Cutting Conventions

- All contexts created using React's `useReducer` hook for complex state management.
- `loading` flags are per-context; long-running secondary actions use distinct flags (`decisionsLoading`, `historyLoading`, etc.).
- Errors are string (user-displayable) or null; raw exceptions are logged to console only.
- Side effects (notifications) use toast notifications inside context actions only for user-triggered pathways.
- Mock fallback pattern: catch network error -> log -> inject deterministic sample -> (optional) user notification of mock usage.

## Detailed Context Contracts

### Auth Context (`AuthContext`)
State: `user: User|null`, `isAuthenticated: boolean`, `loading: boolean`, `error: string|null`.
Actions:
- `login(LoginData)` – Authenticates user and sets session state
- `register(RegisterData)` – Creates new user account
- `registerWithWallet(WalletRegistrationData)` – Wallet-based registration
- `logout()` – Clears user & token state
- `updateUser(userData)` – Updates user profile
Resilience: No mock user provided; failures surface error.
Security: Tokens stored via secure mechanisms only.

### Tokens Context (`TokenContext`)
State: `balance: TokenBalance`, `transactions: TokenTransaction[]`, `loading`, `error`.
Actions:
- `fetchBalance()` – Gets current token balances
- `fetchTransactions()` – Retrieves transaction history
- `transferTokens(TransferData)` – Sends tokens to another address
- `stakeTokens(StakeData)` – Stakes tokens for rewards
Mock Fallback: Random plausible balance + sample transactions on API failure.

### Contributions Context (`ContributionsContext`)
State: `contributions: Contribution[]`, `loading`, `error`.
Actions:
- `fetchContributions(params)` – Gets contributions with optional filtering
- `createContribution(data)` – Submits new contribution
- `verifyContribution(id, verificationData)` – AI-powered verification
- `getContributionExplanation(id)` – Gets AI explanation for contribution

### Wallet Context (`WalletContext`)
State: `wallet: WalletInfo|null`, `connectedWallet`, `transactions`, `isConnecting`, `isLoading`, `error`.
Actions:
- `connectWallet(walletName)` – Connects to Cardano wallet
- `disconnectWallet()` – Disconnects wallet
- `loadWalletInfo()` – Loads wallet balance and info
- `sendTransaction(data)` – Sends ADA transaction
- `sendToken(data)` – Sends token transaction
- `refreshWallet()` – Refreshes wallet data

## Interaction Patterns

| Scenario | Flow | Notes |
|----------|------|-------|
| User authentication | UI -> `auth.login` -> set user state -> redirect | Errors surfaced via context error state |
| Token transfer | UI -> `tokens.transferTokens` -> update balance -> refresh transactions | Optimistic updates with rollback |
| Contribution creation | UI -> `contributions.createContribution` -> add to list -> show success | Immediate UI feedback |
| Wallet connection | UI -> `wallet.connectWallet` -> wallet API -> load data -> UI updates | Handles multiple wallet types |

## Testing Status

✅ **All contexts have comprehensive unit tests** covering:
- Happy path for each public action
- Failure path with mock fallbacks
- Hook integration tests
- Context provider initialization

## Roadmap / Status Summary (Updated September 20, 2025)

### ✅ **COMPLETED**
- ✅ React Context implementation replacing Pinia stores
- ✅ All 4 core contexts fully implemented (Auth, Tokens, Contributions, Wallet)
- ✅ Comprehensive testing infrastructure
- ✅ Mock data fallbacks for all contexts
- ✅ TypeScript interfaces and error handling
- ✅ Context provider hierarchy in App.tsx

### 🚧 **FUTURE ENHANCEMENTS**
- Pagination object in contributions context (when needed)
- Real-time wallet balance updates via WebSocket
- Advanced governance features
- Performance optimizations for large datasets

## Maintenance Checklist
- When adding a new context: update table, describe fallback policy, define actions & side‑effects, add tests, link from `architecture.md`.
- When altering a context contract (rename/remove action): update dependent docs, migrate components.
- All contexts use React patterns and hooks for consistency.

---
Last updated: 2025-09-20
Owner: Frontend Architecture Guild