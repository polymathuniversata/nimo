# Contracts Migration Summary

This document summarizes the migration of Ethereum Solidity contracts to Cardano Aiken equivalents and the archival of original Solidity artifacts.

What changed

- Solidity contracts (e.g., `NimoToken.sol`, `NimoIdentity.sol`, `contracts/src/`, `contracts/script/`, `contracts/test/`) were migrated to Cardano Aiken contracts in `contracts/cardano/`.
- The Aiken equivalents include `contracts/cardano/nimo_token.ak`, `identity_registry.ak`, `contribution_validator.ak`, `metta_bridge.ak`, and related deployment scripts.
- Sensitive configuration files (multiple `.env` files) were sanitized and replaced with `.env.example` templates.

Archive branch

- To preserve the original Solidity artifacts, a branch named `archive/solidity-before-cardano` was created from the pre-migration backup (`backup/final-before-rebase`).
- This branch contains the full Solidity sources and related scripts for audit, reference, or rollback.

Recovery & verification

- To inspect the archived Solidity state locally:

  git fetch origin
  git checkout archive/solidity-before-cardano

- To return to the current migrated state:

  git checkout final

Why we archived instead of keeping files on `final`

- Removing Solidity artifacts from the active `final` branch avoids confusion, avoids deploying the wrong contracts, and reduces maintenance burden. The archive branch preserves history if a rollback or verification is needed.

Next steps

- Run automated tests and CI to validate the Cardano contracts and backend integration.
- Optionally squash WIP commits in `final` for a cleaner history (I can do this on request).

If you want me to squash the WIP commits into the migration commits, or run backend/contract tests now, tell me which option to run next.
