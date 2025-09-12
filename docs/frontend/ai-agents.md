# AI Agents Integration

Canonical documentation for autonomous agent lifecycle, data model, UI surfaces, and extension points. Keep aligned with `AIAgentService` & `aiAgents` store.

## Objectives
- Provide verifiable, explainable automation for contribution validation, fraud detection, reward calculation, governance advisory, and impact analysis.
- Maintain human override capability and audit trails for decisions.
- Support progressive rollout of new agent types with minimal UI churn.

## Domain Model (Frontend)
| Entity | Fields (key) | Notes |
|--------|--------------|-------|
| AIAgent | `id, name, type, status, capabilities, performance{accuracy,responseTime,decisionsMade,successRate}, lastActive, version, model, created_at` | Performance used to derive health score |
| AgentDecision | `id, agentId, agentName, type, targetId, decision, confidence, reasoning, timestamp, status, humanOverride?` | `humanOverride` recorded after override workflow |
| AgentStats | Aggregates: totals, averages, counts (see service) | Derived from `/ai-agents/stats` |
| AgentTrainingData | Training metadata (future UI) | Fetched via `/ai-agents/training` |

## Agent Types
- contribution_verifier – authenticity + evidence weighting
- fraud_detector – anomaly & pattern recognition
- reward_calculator – token award computation
- governance_advisor – proposal analysis (planned UI integration)
- impact_analyzer – long-term socio-economic impact modeling

`AIAgentService.getAgentTypes()` returns label + description; UI should not hardcode.

## Lifecycle Flows
### Standard Fetch Cycle
UI route enter -> store `fetchAgents` (with loading flag) -> fallback mock if network error -> conditionally `fetchStats` & `fetchRecentDecisions` in parallel.

### Decision Override
1. Admin opens decision detail drawer.
2. Provides reason & confirms override.
3. Store calls `overrideDecision(decisionId, {reason, admin})`.
4. Success: refresh decisions; mock path mutates local object.

### Agent Creation
1. User fills create form (name, type, capabilities, model, description).
2. Store `createAgent` -> service POST /ai-agents.
3. On success refresh agent list; mock path synthesizes agent.

## Health Scoring
`AIAgentService.calculateAgentHealth(agent)` combines normalized metrics (accuracy, response time inverse, success rate) with weights (0.4 / 0.3 / 0.3). Status buckets: Excellent ≥80, Good ≥60, Fair ≥40, otherwise Poor. UI color via `getAgentHealthStatus`.

## Store (`aiAgents`)
State: `agents`, `recentDecisions`, `stats`, `loading`, `decisionsLoading`.
Actions & Mapping:
| Action | Service Method | Endpoint | Notes |
|--------|----------------|----------|-------|
| fetchAgents | `fetchAgents` | GET /ai-agents | Mock fallback + Notify |
| fetchRecentDecisions | `fetchAgentDecisions` | GET /ai-agents/decisions | Limit param optional |
| fetchStats | `fetchStats` | GET /ai-agents/stats | Mock fallback |
| createAgent | `createAgent` | POST /ai-agents | Mock fallback injects |
| overrideDecision | `overrideDecision` | POST /ai-agents/decisions/{id}/override | Mock fallback edits local entry |

## UI Surfaces
| Surface | Purpose | Key Components / Routes |
|---------|---------|-------------------------|
| Agents Dashboard | List agents + KPIs + health | `/dashboard/admin` section or `/agents` (future) |
| Decisions Feed | Recent agent decisions sortable/filterable | `AgentDecisionsTable.vue` (planned) |
| Agent Detail Panel | Performance, capabilities, health, recommendations | Drawer / dialog component |
| Creation Modal | Provision new agent | `CreateAgentForm.vue` (planned) |
| Override Workflow | Human override with reason & traceability | `DecisionOverrideDialog.vue` (planned) |

## Extensibility Points
| Need | Pattern |
|------|---------|
| Real-time decisions | SSE/WebSocket stream -> append to `recentDecisions` (TODO) |
| Agent training UI | Expose `fetchTrainingData` + timeline component |
| Performance trends | Use `fetchPerformanceMetrics` + charts (Sparkline) |
| Recommendation engine | `getRecommendedActions(agent)` per row badge |

## Error & Fallback Strategy
- Primary fetch actions fallback to canonical deterministic mock data enabling UI development offline.
- Notify user only once when mock agent data loaded (avoid spam).
- Decision override fallback marks status `overridden` and attaches `humanOverride` object.

## Security & Governance
- Agent creation, status toggle, training, overrides require elevated role (backend enforced). UI should hide actions if user lacks admin/validator capability.
- All overrides must include `reason` + `admin` identifier → audit trail.

## Suggested Test Coverage
- Health score computation for boundary values (fast vs slow response time).
- Override path modifies local decision in mock mode.
- Agent creation adds entry with expected defaults.
- Recommendation actions for agents with poor metrics.

## Roadmap / TODOs
- Stream ingestion for decisions.
- Dedicated performance trends panel.
- Training dataset management UI.
- Governance advisor output explanation view.

---
Last updated: 2025-09-07
Owner: Frontend Architecture Guild