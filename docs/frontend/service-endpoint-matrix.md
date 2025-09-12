# Service ↔ API Endpoint Matrix

Authoritative map of frontend service methods & store actions to backend HTTP endpoints. This is the contract layer; changes require doc update + coordination with backend before merge.

## Legend
- Method: `service.method()` or `store.action()`
- HTTP: VERB /path (variables in `{}`)
- Auth: (A)=Requires Auth Header / token; (P)=public; (R)=role/permission gated
- Mock: Y = currently supplies mock/fallback data client-side when failing or unimplemented.
- Status: `ok` (implemented and used), `planned` (documented but not yet implemented), `stub` (throws / returns placeholder), `deprecated` (scheduled removal).

## Core Domains

### Authentication
| Method | HTTP | Auth | Status | Mock | Notes |
|--------|------|------|--------|------|-------|
| `auth.login` | POST /auth/login | P | ok | N | Sets access+refresh via secureTokenService |
| `auth.register` | POST /auth/register | P | ok | N | Does not auto-authenticate |
| `auth.registerWithWallet` | POST /auth/register/wallet | P | ok | N | Combines identity + wallet binding |
| `auth.logout` | (client only) | A | ok | N | Clears token & session |

### Tokens / Economics
| Method | HTTP | Auth | Status | Mock | Notes |
|--------|------|------|--------|------|-------|
| `tokens.fetchBalance` | GET /tokens/balance | A | ok | Y | Random fallback (dev) – remove for prod |
| `tokens.fetchTransactions` | GET /tokens/transactions (planned) | A | planned | Y | Currently hardcoded list in store |
| `tokens.transferTokens` | POST /tokens/transfer | A | ok | N | Refreshes balance + tx afterwards |
| `tokens.stakeTokens` | POST /tokens/stake | A | ok | N | Refreshes balance |
| `tokenService.getTokenBalance` | wallet asset scan | A | ok | N | Uses wallet API, not REST |
| `tokenService.transferTokens` | (Cardano tx build + submit) | A | ok | N | On-chain transaction via mesh sdk |
| `tokenService.mintTokens` | (future contract) | A/R | stub | N | Throws until contract integration |
| `tokenService.burnTokens` | (future contract) | A/R | stub | N | Throws until contract integration |
| `tokenService.getTransactionHistory` | (future) | A | planned | N | Returns [] placeholder |

### Contributions
| Method | HTTP | Auth | Status | Mock | Notes |
|--------|------|------|--------|------|-------|
| `contributions.fetchContributions` | GET /contributions | A | ok | Y | Params: page, per_page, filters |
| `contributions.createContribution` | POST /contributions/ | A | ok | N | Prepend on success |
| `contributions.verifyContribution` | POST /contributions/{id}/verify | A/R | ok | N | Requires verifier role (enforced backend) |
| `contributions.getContributionExplanation` | GET /contributions/{id}/explain | A | ok | N | AI explanation endpoint |

### AI Agents
| Method | HTTP | Auth | Status | Mock | Notes |
|--------|------|------|--------|------|-------|
| `aiAgentService.fetchAgents` | GET /ai-agents | A | ok | Y | Store substitutes mock on failure |
| `aiAgentService.getAgentById` | GET /ai-agents/{id} | A | ok | N |  |
| `aiAgentService.fetchAgentDecisions` | GET /ai-agents/decisions | A | ok | Y | Limit param supported |
| `aiAgentService.fetchStats` | GET /ai-agents/stats | A | ok | Y | Mock stats on failure |
| `aiAgentService.fetchPerformanceMetrics` | GET /ai-agents/performance | A | ok | N |  |
| `aiAgentService.fetchTrainingData` | GET /ai-agents/training | A | ok | N |  |
| `aiAgentService.createAgent` | POST /ai-agents | A/R | ok | Y | Mock success fallback adds local agent |
| `aiAgentService.updateAgent` | PUT /ai-agents/{id} | A/R | ok | N |  |
| `aiAgentService.toggleAgentStatus` | PATCH /ai-agents/{id}/status | A/R | ok | N |  |
| `aiAgentService.trainAgent` | POST /ai-agents/{id}/train | A/R | ok | N |  |
| `aiAgentService.overrideDecision` | POST /ai-agents/decisions/{id}/override | A/R | ok | Y | Mock override sets decision.humanOverride |

### Bonds (Impact Investment)
| Method | HTTP | Auth | Status | Mock | Notes |
|--------|------|------|--------|------|-------|
| `bondService.fetchActiveBonds` | GET /bonds/active | A | ok | Y | Mock list if failure |
| `bondService.fetchMyInvestments` | GET /bonds/my-investments | A | ok | Y | Mock list if failure |
| `bondService.fetchStats` | GET /bonds/stats | A | ok | Y | Mock stats if failure |
| `bondService.createBond` | POST /bonds | A/R | ok | Y | Fallback constructs local bond |
| `bondService.investInBond` | POST /bonds/{id}/invest | A | ok | Y | Fallback updates local funding |
| `bondService.getBondById` | GET /bonds/{id} | A | ok | N |  |
| `bondService.getBondsByCategory` | GET /bonds?category= | A | ok | N |  |
| `bondService.getBondsByLocation` | GET /bonds?location= | A | ok | N |  |
| `bondService.getInvestmentById` | GET /bonds/investments/{id} | A | ok | N |  |

### Governance
| Method | HTTP | Auth | Status | Mock | Notes |
|--------|------|------|--------|------|-------|
| `governance.fetchActiveProposals` | GET /governance/proposals/active | A | ok | Y | Store fallback sample proposals |
| `governance.fetchProposalHistory` | GET /governance/proposals/history | A | ok | Y |  |
| `governance.fetchStats` | GET /governance/stats | A | ok | Y | Mock stats if failure |
| `governance.fetchUserStats` | GET /governance/user/stats | A | ok | Y |  |
| `governance.fetchGovernanceParams` | GET /governance/params | A | ok | N | Defaults kept if fail |
| `governance.createProposal` | POST /governance/proposals | A/R | ok | Y | Mock success fallback |
| `governance.voteOnProposal` | POST /governance/proposals/{id}/vote | A | ok | Y | Mock optimistic update |
| `votingService.getUserVotingPower` | GET /governance/user/voting-power | A | ok | Y | Default 1 on fail |

### Wallet / Cardano Integration
| Method | HTTP | Auth | Status | Mock | Notes |
|--------|------|------|--------|------|-------|
| `cardanoWallet.connectWallet` | browser wallet API | A | ok | N | Not REST; CIP-30 adapter |
| `cardanoWallet.disconnectWallet` | browser wallet API | A | ok | N |  |
| `cardanoWallet.loadWalletInfo` | GET /cardano/wallet (planned) | A | planned | N | Attempts backend sync |
| `cardanoWallet.loadTransactions` | GET /cardano/tx (planned) | A | planned | N | Placeholder until backend ready |
| `cardanoWallet.sendTransaction` | POST /cardano/tx (planned) | A | planned | N | Currently on-chain only |
| `cardanoWallet.sendToken` | POST /cardano/token-tx (planned) | A | planned | N |  |
| `cardanoWallet.refreshWallet` | composite | A | ok | N | Calls wallet + (planned) backend |
| `cardanoWallet.checkConnection` | GET /cardano/status (planned) | A | planned | N | Graceful if missing |

## Gaps & Actions
| Gap | Impact | Plan |
|-----|--------|------|
| `tokens.fetchTransactions` lacks real endpoint | Inconsistent history display | Implement /tokens/transactions backend; remove mock path |
| Token mint/burn stubbed | Admin tooling blocked | Define contract, implement with policy script integration |
| Wallet backend endpoints (planned) absent | No persisted tx metadata | Add minimal read-only wallet status & tx history endpoints |
| SSE/WebSocket for agent decisions not documented | No real-time updates | Introduce /ai-agents/decisions/stream (SSE) – future doc update |
| Governance optimistic vote not implemented | Slower perceived responsiveness | Add local optimistic mutation + rollback on failure |

## Change Control
- Any endpoint path change MUST update: this matrix, affected service file, related store, and `routing-map.md` if navigation impacted.
- Additions require test stubs referencing new method + matrix entry.

---
Last updated: 2025-09-07
Owner: Frontend Architecture Guild