# MeTTa Rules for Nimo Platform

This directory contains MeTTa rule definitions used by the Nimo platform's reasoning engine.

## Overview

MeTTa (Meta Type Talking) is a symbolic reasoning language that powers the autonomous decision-making in Nimo. The rules in this directory enable the platform to verify contributions, calculate reputation scores, detect fraud, and determine token awards.

## Files

- `core_rules.metta`: Core MeTTa rules for contribution verification, reputation scoring, and token award calculations.

## How to Use

These rules are loaded automatically by the MeTTa services:

- `MeTTaReasoning` service in `backend/services/metta_reasoning.py` 
- `MeTTaIntegration` service in `backend/services/metta_service.py`

The services initialize the MeTTa space and evaluate these rules for autonomous decision-making.

## Updated Atom-Based Approach

Based on research findings in `docs/metta_research_findings.md`, we've updated our MeTTa integration to use an atom-based approach rather than object-based:

**Old approach (object-based):**
```metta
(verify-contribution (parse-json "{\"user\":\"123\",\"skills\":[\"coding\"]}") 
                     (parse-json "{\"type\":\"education\"}"))
```

**New approach (atom-based):**
```metta
(VerifyContribution "contrib-123")
```

This approach offers better performance, readability, and maintainability.

## Extending Rules

To extend or customize the MeTTa reasoning capabilities:

1. Add new rules to `core_rules.metta`
2. Ensure rule naming follows atom-based conventions (e.g., `(VerifyContribution)` instead of `(verify-contribution)`)
3. Run tests to ensure the new rules work correctly

## Rule Categories

- **Identity & User Management**: Rules for user identity verification
- **Contribution Verification**: Rules for validating contributions using various evidence types
- **Impact Assessment**: Rules for evaluating the impact level of contributions
- **Confidence Scoring**: Rules for calculating confidence in verification decisions
- **Explanation Generation**: Rules for generating human-readable explanations
- **Fraud Detection**: Rules for detecting potential fraud or duplicate submissions
- **Token Award Calculation**: Rules for determining token rewards
- **Reputation Calculation**: Rules for calculating user reputation scores

## Example Rules

### Atom-Based Verification

```metta
; Verification rule with confidence scoring
(= (VerifyContribution $contrib-id)
   (and (Contribution $contrib-id $user-id $_)
        (ValidEvidence $contrib-id)
        (SkillMatch $contrib-id $user-id)
        (ImpactAssessment $contrib-id "moderate")))

; Evidence validation
(= (ValidEvidence $contrib-id)
   (let* (($evidence-count (CountEvidence $contrib-id))
          ($min-evidence 1))
     (>= $evidence-count $min-evidence)))
```

### Dynamic Token Award Calculation

```metta
; Dynamic token award based on evidence and verification
(= (CalculateTokenAward $contrib-id)
   (let* (($category (GetContributionCategory $contrib-id))
          ($base-amount (BaseTokenAmount $category))
          ($confidence (CalculateConfidence $contrib-id))
          ($quality-bonus (* $confidence 50))
          ($total-amount (+ $base-amount $quality-bonus)))
     $total-amount))
```

For more information, see the [MeTTa Research Findings](../docs/metta_research_findings.md) document.