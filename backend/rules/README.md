# MeTTa Rules for Nimo Platform

This directory contains MeTTa rule definitions used by the Nimo platform's reasoning engine.

## Overview

MeTTa (Meta Type Talking) is a symbolic reasoning language that powers the autonomous decision-making in Nimo. The rules in this directory enable the platform to verify contributions, calculate reputation scores, detect fraud, determine token awards, and manage complex autonomous operations.

## Files

### Core Rule Files
- `core_rules.metta`: Core MeTTa rules for contribution verification, reputation scoring, and token award calculations.
- `metta_example.metta`: Example MeTTa script demonstrating identity and contribution verification patterns.

### Advanced Rule Files
- `enhanced_rules.metta`: Advanced multi-factor verification, fraud detection, dynamic token awards, adaptive thresholds, and predictive analytics.
- `autonomous_awards.metta`: Intelligent, ML-driven, market-adjusted, and gamified token award systems.
- `fraud_detection.metta`: Comprehensive fraud detection system with behavioral analysis, content fraud detection, network analysis, and adaptive security measures.
- `adaptive_governance.metta`: Decentralized governance system with adaptive thresholds, stakeholder management, reputation evolution, and community health monitoring.
- `predictive_analytics.metta`: Advanced predictive modeling, feature engineering, ML pipeline management, real-time predictions, and model explainability.
- `integration_orchestration.metta`: Cross-platform integration, API orchestration, blockchain interoperability, and service mesh management.

### Master Orchestration
- `unified_autonomous_system.metta`: Master MeTTa rules that orchestrate all autonomous platform functions including integrated contribution processing, predictive platform management, autonomous governance cycles, and comprehensive security management.

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

## Rule Categories

### Core Functionality
- **Identity & User Management**: Rules for user identity verification
- **Contribution Verification**: Rules for validating contributions using various evidence types
- **Impact Assessment**: Rules for evaluating the impact level of contributions
- **Confidence Scoring**: Rules for calculating confidence in verification decisions
- **Explanation Generation**: Rules for generating human-readable explanations
- **Fraud Detection**: Rules for detecting potential fraud or duplicate submissions
- **Token Award Calculation**: Rules for determining token rewards
- **Reputation Calculation**: Rules for calculating user reputation scores

### Advanced Features
- **Multi-Factor Verification**: Enhanced verification using multiple evidence sources
- **Behavioral Analysis**: User behavior pattern analysis and anomaly detection
- **Content Fraud Detection**: Plagiarism, synthetic content, and spam detection
- **Network Analysis**: Sybil attack detection and collusion identification
- **Adaptive Governance**: Dynamic governance with stakeholder management
- **Predictive Analytics**: ML-based predictions and trend analysis
- **Cross-Platform Integration**: API orchestration and blockchain interoperability

### Autonomous Systems
- **Autonomous Award Systems**: ML-driven, market-adjusted token awards
- **Predictive Platform Management**: Performance prediction and optimization
- **Autonomous Governance**: Self-evolving governance systems
- **Integrated Security Management**: Comprehensive threat detection and response
- **Continuous Learning**: Adaptive learning and system optimization

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

### Advanced Fraud Detection

```metta
; Comprehensive fraud detection
(= (DetectFraudComprehensive $contrib-id)
   (or (DetectFraudEnhanced $contrib-id)
       (BehavioralAnomalyDetection $contrib-id)
       (ContentFraudDetection $contrib-id)
       (NetworkFraudDetection $contrib-id)))
```

### Autonomous Governance

```metta
; Adaptive governance decision making
(= (MakeGovernanceDecision $proposal-id)
   (let* (($proposal-details (GetProposalDetails $proposal-id))
          ($stakeholder-votes (CollectStakeholderVotes $proposal-id))
          ($community-sentiment (AnalyzeCommunitySentiment $proposal-id))
          ($decision-weights (CalculateDecisionWeights $proposal-details))
          ($final-decision (WeightedDecision $stakeholder-votes $community-sentiment
                                           $expert-opinions $decision-weights)))
     $final-decision))
```

## Extending Rules

To extend or customize the MeTTa reasoning capabilities:

1. Add new rules to the appropriate rule file based on functionality
2. Ensure rule naming follows atom-based conventions (e.g., `(VerifyContribution)` instead of `(verify-contribution)`)
3. Update the master orchestration file if creating new autonomous functions
4. Run tests to ensure the new rules work correctly
5. Update this README with new rule categories and examples

## Integration with Backend Services

The MeTTa rules integrate with the following backend components:

- **MeTTa Integration Service**: Loads and executes rules for autonomous operations
- **Enhanced MeTTa Service**: Provides advanced reasoning capabilities
- **Autonomous Award System**: Uses ML-driven rules for token calculations
- **Fraud Detection Engine**: Applies comprehensive fraud detection rules
- **Governance Engine**: Implements adaptive governance rules
- **Predictive Analytics Engine**: Uses ML and predictive rules

## Performance Considerations

- Rules are optimized for atom-based execution
- Complex rules use `let*` for efficient variable binding
- Recursive rules include termination conditions
- Large datasets are processed using streaming patterns
- Caching is implemented for frequently used rule results

## Testing and Validation

- Unit tests for individual rules in `backend/tests/`
- Integration tests for rule orchestration
- Performance benchmarks for complex rule evaluation
- Validation of autonomous decision accuracy

For more information, see the [MeTTa Research Findings](../docs/metta_research_findings.md) document.