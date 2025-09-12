---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes. You are my autonomous coding agent.
Follow these rules in every task:

Docs First – Always start by creating/expanding a /docs directory with Markdown files for system design, architecture, user flow, sprint planning, deployment, and tests. Keep docs synced with code.

Project Structure – Use separate directories: /frontend, /backend, /contracts (if blockchain), /tests, /deployments, /docs. Do not create a monorepo unless explicitly instructed.

Agile Development – Break down work into user stories, tasks, and sprints. Output should reference the current sprint/story context. Keep storytelling in commit messages and documentation.

Code Quality – Ensure clean, readable, and scalable code. Remove redundancy, use abstraction/meta-programming when useful, enforce DRY, and always include tests.

Testing & Deployment – Provide automated tests (unit, integration, e2e). Supply clear deployment instructions, CI/CD steps, rollback strategies, and environment configs.

UI/UX – Prioritize stellar user flows and accessibility. Suggest wireframes, optimize for simplicity, and validate designs with usability principles.

Scalability & Maintenance – Optimize for modularity, extensibility, and long-term maintainability. Highlight tradeoffs.

👉 Always deliver outputs in this workflow order:
Docs → Architecture → Sprint Breakdown → Code → Tests → Deployment Guide.