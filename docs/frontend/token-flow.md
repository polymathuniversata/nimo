# Token & Wallet Flow

Authoritative description of how the frontend orchestrates Cardano wallet connectivity, token discovery, NIMO balance operations, and REST ↔ on‑chain interplay. Update this doc when adding new wallet actions, token op types, or backend sync endpoints.

## Goals
- Clean separation between UI components, Pinia wallet store, domain services, and low-level CIP-30 wallet APIs.
- Graceful degradation when backend endpoints (status, tx history) are unavailable.
- Deterministic user experience for connect / refresh / transfer flows.

## Layered Responsibilities
| Layer | Responsibility | Files |
|-------|----------------|-------|
| UI Components | Trigger connect, show balances, submit transfer forms | `components/wallet/*`, pages referencing wallet buttons |
| Store (`cardanoWallet`) | Reactive state, orchestration, throttled refresh, error channel | `stores/cardanoWallet.ts` |
| Token Service | On-chain token-level operations (transfer, balance extraction) + validation | `services/TokenService.ts` |
| Wallet Connection Adapter | Detect & interact with injected wallets (CIP-30), formatting helpers | `services/walletConnection.ts` |
| Backend (planned) | Persist tx metadata, aggregate history, risk flags | (future `/cardano/*` endpoints) |

## Connection Lifecycle
1. User clicks Connect (with chosen wallet key e.g. `nami`).
2. Store action `connectWallet(walletName)` calls `walletConnectionService.connectWallet`.
3. On success, optional backend sync attempt via `cardanoService.connectWallet` (non-fatal if fails).
4. Store loads transactions (`loadTransactions`) + wallet info concurrently.
5. `isConnected` getter flips true → UI renders balance & actions.

Sequence (current, simplified):
UI -> store.connectWallet -> walletConnectionService (CIP-30) -> (backend sync attempt) -> store.loadTransactions -> reactive UI updates

## Refresh Logic
- `refreshWallet` requires `canRefresh` (>=30s since last refresh) to avoid spamming.
- Invokes (if connected): wallet adapter refresh + parallel backend wallet info & tx history fetch.
- On success updates `lastRefresh`; on failure warns & retains stale data.

## Balance & Token Discovery
- `tokenService.getTokenBalance` queries asset list from connected wallet instance (CIP-30 / Mesh SDK abstraction).
- Filters assets for those containing hex policy snippet `4e494d4f` (ASCII: NIMO). TODO: Centralize actual policy ID constant.
- Formats balance dividing by 1e6 (assumed decimals). TODO: Confirm decimal precision from contract metadata.

## Transfer Flow (NIMO)
1. User submits form (recipient address, amount).
2. Component calls `tokenService.transferTokens(walletRef, recipient, amount)`.
3. Service validates operation via `TokenOperationValidator` (from `ServiceFactory`).
4. Builds transaction with `@meshsdk/core` Transaction, adds asset, signs, submits.
5. Returns `txHash` to UI for display; UI may push into optimistic history (future enhancement).

Error Modes:
- Wallet not connected → immediate thrown error (UI should catch & prompt connect).
- Validation failure → thrown error with user-friendly message.
- Submission failure (network/node) → thrown error; no state mutation.

## Mint / Burn (Future)
Current methods `mintTokens`, `burnTokens` throw with explanatory message. Prerequisites:
- Policy script integration & key management.
- Backend orchestration endpoint or secure in-browser policy signing (discouraged).
- Audit & permission gating (admin / governance controlled).

## Planned Backend Endpoints
| Endpoint | Purpose | Status | Notes |
|----------|---------|--------|-------|
| GET /cardano/status | Connection health, network id, backend observed address | planned | Used by `checkConnection` |
| GET /cardano/wallet | Aggregated balances, identified NIMO holdings | planned | Supplements CIP-30 views |
| GET /cardano/tx | Paginated tx history + metadata labels | planned | Enables richer history than local adapter |
| POST /cardano/tx | Server-assisted submission / metadata enrichment | planned | Optional if direct submit slow |
| POST /cardano/token-tx | Server-assisted multi-asset send | planned |  |

## Store vs Service Boundary
| Concern | Store | Service |
|---------|-------|---------|
| Reactive flags (loading, isConnecting) | yes | no |
| Retry / throttling policy | store (refresh window) | service (handleRequest) |
| Wallet enumeration | store (detect) | adapter (low-level) |
| Transaction building | no | `TokenService` |
| Validation semantics | no | `TokenOperationValidator` |
| User notifications | store (Notify on success/fail) | no (logs only) |

## State Diagram (Textual)
State: Disconnected → Connecting → Connected (Synced | Partially Synced) → Refreshing → Connected.
Failure branch: Connecting → Error (retain Disconnected) OR Refreshing → Connected (error flagged).

## Error Handling Strategy
- All critical path actions throw; components must wrap with try/catch and surface toast/dialog.
- Store also sets `error` ref for reactive banners.
- Non-critical backend sync failures log to console + continue (never block wallet display if CIP-30 success).

## Security Considerations
- No private keys touch our code; CIP-30 wallet handles signing.
- Avoid storing raw addresses in localStorage beyond session; rely on store state.
- Validate recipient addresses (`walletConnectionService.validateAddress`).
- Rate limit refresh operations.

## Observability (Planned)
- Add instrumentation around connect, refresh, transfer success/failure counts.
- Emit custom events `wallet:connected`, `wallet:transfer_submitted`, `wallet:refresh` for analytics.

## Open TODOs
- Policy ID constant centralization.
- Real transaction history ingestion & caching.
- Optimistic UI update for transfers with pending status.
- Mint/Burn governance gating design.
- SSE/WebSocket channel for real-time balance changes (optional).

---
Last updated: 2025-09-07
Owner: Frontend Architecture Guild