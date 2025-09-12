# Frontend Testing Strategy

Authoritative plan for automated verification of the frontend. Align changes here before adding large swaths of tests. Targets: determinism, fast feedback (<90s unit+component), confidence in critical economic & governance flows.

## Test Pyramid
| Layer | Purpose | Tooling | Target Ratio |
|-------|---------|---------|--------------|
| Unit | Pure functions, store actions (logic), service helpers | Vitest + ts-jest-like transformers (native TS) | 55% |
| Component (shallow) | Render + props + emitted events | Vitest + @vue/test-utils + Quasar test utils | 20% |
| Integration (store+service) | Store action calling mocked service -> state mutation | Vitest + custom mocks | 15% |
| Visual/Story | Design token & component regression | Storybook + Chromatic (future) | 5% |
| E2E (critical paths) | Happy path user journeys | Playwright (planned) | 5% |

## Scope & Coverage Priorities
1. Economic correctness (token transfer, stake flows) – ensure no silent failures.
2. AI agent decision override integrity & health score accuracy.
3. Governance voting and proposal creation logic.
4. Bond investment validation boundaries.
5. Wallet connection guard rails (error states, refresh throttle).
6. Design system primitives (spacing function, token mapping) – minimal snapshot.

## Tooling Stack
- Test Runner: Vitest (`vitest.config.ts`).
- Assertions: Chai (bundled) + custom matchers.
- Vue Utils: `@vue/test-utils` with Quasar plugin factory.
- Mocking: Native Vitest mocks + manual service singleton injection.
- Coverage: c8 instrumentation -> output to `coverage/` (lcov + text-summary).
- Lint on Test: Pre-commit hook recommended (TODO) to prevent style regressions.

## Conventions
| Rule | Rationale |
|------|-----------|
| One describe block per function/store action grouping | Clarity |
| No snapshot testing for large components (except design tokens) | Avoid brittle tests |
| Mock network at service boundary; do not stub inside store logic | Preserve behavior |
| Use explicit data builders (factory functions) for complex entities | Consistency |
| Avoid time-based sleeps; use deterministic promises | Speed |

## Example: Store Action Test (Tokens)
```ts
import { setActivePinia, createPinia } from 'pinia'
import { useTokensStore } from '@/stores/tokens'

vi.mock('@/boot/axios', () => ({
  api: {
    get: vi.fn().mockResolvedValue({ data: { balance: 1234 } })
  }
}))

describe('tokens store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('fetchBalance sets balance and clears error', async () => {
    const store = useTokensStore()
    store.balance = 0
    store.error = 'previous'

    await store.fetchBalance()

    expect(store.balance).toBe(1234)
    expect(store.error).toBeNull()
  })
})
```

## Example: Health Score Utility
Test weights & normalization boundaries for `calculateAgentHealth` by injecting crafted performance metrics.

## Component Test Pattern
1. Provide minimal required props.
2. Mount with Quasar plugin stub (theme + notify).
3. Interact (emit events) and assert emitted payload & DOM reflect state.

```ts
import { mount } from '@vue/test-utils'
import AgentCard from '@/components/agents/AgentCard.vue'

const agent = {/* minimal stub matching AIAgent interface */}

test('renders agent name & health badge', () => {
  const wrapper = mount(AgentCard, { props: { agent } })
  expect(wrapper.text()).toContain(agent.name)
  expect(wrapper.find('[data-test="health-badge"]').exists()).toBe(true)
})
```

## Integration Test: Bond Investment
Mock service `investInBond` success & error; assert store updates funding progress and investment list.

## Visual Regression (Planned)
- Add Storybook stories for: spacing scale, color palette, token balance widget, agent card, bond progress bar.
- Integrate Chromatic or Percy for PR diff gating (TODO Q4).

## E2E (Planned)
| Journey | Steps | Notes |
|---------|-------|-------|
| Auth + Dashboard | register -> login -> redirect -> dashboard metrics visible | Smoke gate |
| Contribution Flow | login -> create contribution -> verify (mock) | Ensures core interaction |
| Token Transfer | connect wallet (mock) -> transfer -> balance updates | Requires wallet mock harness |
| Bond Invest | list -> select -> invest -> portfolio view updated | Validates economic flow |

## Performance Testing
- Use a perf harness to simulate rendering 100 bond cards; ensure <500ms mount (local dev target). (TODO separate doc if needed)

## CI Integration (Planned)
| Stage | Command | Artifact |
|-------|---------|----------|
| Lint | `npm run lint` | Problem matcher |
| Unit + Component | `npm run test:unit -- --coverage` | Coverage report (threshold gate) |
| Build | `npm run build` | Dist bundle size metrics |
| Storybook | `npm run build-storybook` | Static site |

## Coverage Targets (Initial)
| Area | Target % |
|------|----------|
| Statements | 70 |
| Branches | 60 |
| Functions | 70 |
| Lines | 70 |

Raise targets once baseline stable.

## Risk-based Exclusions
- Vendor-generated files.
- Pure style-only components (visual diff only).
- Legacy wallet stores (to be deprecated) – minimal tests just ensuring no break until removal.

## Open TODOs
- Add factories: `tests/factories/agentFactory.ts`, `bondFactory.ts`, `proposalFactory.ts`.
- Create Quasar test plugin util.
- Implement coverage threshold gating in CI.
- Introduce Playwright config + smoke spec.

---
Last updated: 2025-09-07
Owner: Frontend Architecture Guild