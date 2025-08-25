# MeTTa Integration in Frontend Components
**Implementation Plan and UI Components: August 25, 2025**

## Overview

This document outlines how we will integrate MeTTa reasoning results and autonomous agent decisions into the frontend user interface. The goal is to provide users with transparent explanations for how contribution verifications, token awards, and reputation calculations are made by the MeTTa autonomous agents.

## MeTTa Concepts in the UI

MeTTa is the reasoning system behind Nimo's autonomous decisions. The frontend needs to visualize:

1. **Reasoning Chains** - How MeTTa reached verification decisions
2. **Token Calculations** - How reputation tokens are calculated
3. **Verification Confidence** - Confidence scores for AI decisions
4. **Impact Assessment** - How contributions are evaluated for impact

## UI Components for MeTTa Integration

### 1. Verification Reasoning Card

This component will display the MeTTa reasoning chain for contribution verification:

```vue
<!-- components/metta/VerificationReasoningCard.vue -->
<template>
  <q-card class="reasoning-card">
    <q-card-section>
      <div class="text-h6">Verification Reasoning</div>
      <div class="text-subtitle2">How this contribution was verified</div>
    </q-card-section>
    
    <q-card-section>
      <div class="reasoning-chain">
        <div v-for="(step, index) in reasoning.steps" :key="index" class="reasoning-step">
          <q-chip :color="getStepColor(step)" text-color="white" class="step-chip">
            {{ step.type }}
          </q-chip>
          <div class="step-content">{{ step.explanation }}</div>
          <div class="step-confidence">Confidence: {{ step.confidence }}%</div>
        </div>
      </div>
    </q-card-section>
    
    <q-card-section>
      <div class="text-subtitle1">Final Decision</div>
      <div class="final-decision" :class="reasoning.verified ? 'verified' : 'rejected'">
        {{ reasoning.verified ? 'Verified' : 'Not Verified' }} 
        ({{ reasoning.confidence }}% confidence)
      </div>
      <div class="metta-hash text-caption">
        MeTTa Proof Hash: {{ shortenHash(reasoning.mettaProofHash) }}
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  reasoning: {
    type: Object,
    required: true
  }
})

const getStepColor = (step) => {
  if (step.type === 'Evidence Analysis') return 'blue'
  if (step.type === 'Skills Verification') return 'green'
  if (step.type === 'Reputation Check') return 'purple'
  if (step.type === 'Impact Assessment') return 'orange'
  return 'grey'
}

const shortenHash = (hash) => {
  if (!hash) return ''
  return `${hash.substring(0, 8)}...${hash.substring(hash.length - 8)}`
}
</script>
```

### 2. Token Award Explanation

This component will visualize how MeTTa calculated token awards:

```vue
<!-- components/metta/TokenAwardExplanation.vue -->
<template>
  <q-card class="token-award-card">
    <q-card-section>
      <div class="text-h6">Token Award Calculation</div>
      <div class="token-amount">
        <q-icon name="token" size="24px" color="primary" />
        <span class="text-h5">{{ tokenAward.totalAmount }} NIMO</span>
      </div>
    </q-card-section>
    
    <q-card-section>
      <q-list separator>
        <q-item v-for="(factor, index) in tokenAward.factors" :key="index">
          <q-item-section avatar>
            <q-icon :name="getFactorIcon(factor.type)" :color="getFactorColor(factor.type)" />
          </q-item-section>
          
          <q-item-section>
            <q-item-label>{{ factor.name }}</q-item-label>
            <q-item-label caption>{{ factor.explanation }}</q-item-label>
          </q-item-section>
          
          <q-item-section side>
            <div class="factor-amount" :class="factor.multiplier >= 1 ? 'positive' : 'negative'">
              <span v-if="factor.multiplier >= 1">+</span>{{ factor.amount }} NIMO
              <div class="factor-multiplier">×{{ factor.multiplier }}</div>
            </div>
          </q-item-section>
        </q-item>
      </q-list>
    </q-card-section>
    
    <q-card-section>
      <div class="text-subtitle1">Verification Method</div>
      <div class="verification-method">
        {{ tokenAward.verificationMethod }}
        <q-tooltip>
          {{ tokenAward.verificationMethodDescription }}
        </q-tooltip>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  tokenAward: {
    type: Object,
    required: true
  }
})

const getFactorIcon = (type) => {
  if (type === 'base') return 'monetization_on'
  if (type === 'skill') return 'engineering'
  if (type === 'impact') return 'trending_up'
  if (type === 'complexity') return 'psychology'
  if (type === 'verification') return 'verified'
  if (type === 'bonus') return 'stars'
  return 'token'
}

const getFactorColor = (type) => {
  if (type === 'base') return 'primary'
  if (type === 'skill') return 'green'
  if (type === 'impact') return 'orange'
  if (type === 'complexity') return 'purple'
  if (type === 'verification') return 'teal'
  if (type === 'bonus') return 'amber'
  return 'grey'
}
</script>
```

### 3. Reputation Scoring Visualization

This component will visualize the MeTTa reputation scoring system:

```vue
<!-- components/metta/ReputationScoreCard.vue -->
<template>
  <q-card class="reputation-card">
    <q-card-section class="reputation-header">
      <div>
        <div class="text-h6">Reputation Score</div>
        <div class="text-subtitle2">Based on your verified contributions</div>
      </div>
      <div class="reputation-score">{{ reputationData.totalScore }}</div>
    </q-card-section>
    
    <q-card-section>
      <div class="categories-container">
        <div 
          v-for="category in reputationData.categories" 
          :key="category.name"
          class="category-item"
        >
          <div class="category-label">{{ category.name }}</div>
          <q-linear-progress
            :value="category.score / 100"
            :color="getCategoryColor(category.name)"
            rounded
            class="category-progress"
          />
          <div class="category-score">{{ category.score }}</div>
        </div>
      </div>
    </q-card-section>
    
    <q-card-section>
      <div class="text-subtitle2">MeTTa Reputation Formula</div>
      <div class="formula-container">
        <div class="formula-text">{{ reputationData.formula }}</div>
        <q-tooltip>
          {{ reputationData.formulaExplanation }}
        </q-tooltip>
      </div>
    </q-card-section>
    
    <q-card-section>
      <q-expansion-item
        label="How is your reputation calculated?"
        header-class="text-primary"
      >
        <q-card>
          <q-card-section>
            <div v-for="(step, index) in reputationData.calculationSteps" :key="index" class="calculation-step">
              <div class="step-number">{{ index + 1 }}</div>
              <div class="step-description">{{ step }}</div>
            </div>
          </q-card-section>
        </q-card>
      </q-expansion-item>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  reputationData: {
    type: Object,
    required: true
  }
})

const getCategoryColor = (category) => {
  const colors = {
    'Technical': 'blue',
    'Community': 'green',
    'Leadership': 'purple',
    'Education': 'teal',
    'Activism': 'orange'
  }
  return colors[category] || 'grey'
}
</script>
```

### 4. MeTTa Decision Explainer Component

This component will provide users with explanations about automated MeTTa decisions:

```vue
<!-- components/metta/DecisionExplainer.vue -->
<template>
  <q-card class="decision-explainer">
    <q-card-section class="decision-header">
      <q-avatar size="36px">
        <img src="~assets/metta-logo.png" alt="MeTTa AI">
      </q-avatar>
      <div class="decision-title">
        <div class="text-subtitle1">MeTTa Decision Explainer</div>
        <div class="text-caption">Autonomous reasoning explanation</div>
      </div>
    </q-card-section>
    
    <q-card-section>
      <div class="decision-summary">
        <div class="decision-type">{{ decision.type }}</div>
        <div class="decision-result" :class="decision.result">
          {{ formatDecisionResult(decision.result) }}
        </div>
      </div>
      
      <div class="explanation-text">{{ decision.explanation }}</div>
      
      <q-timeline color="secondary">
        <q-timeline-entry
          v-for="(rule, index) in decision.rules"
          :key="index"
          :title="rule.name"
          :subtitle="rule.description"
          :color="rule.satisfied ? 'positive' : 'negative'"
          :icon="rule.satisfied ? 'check_circle' : 'cancel'"
        >
          <div class="rule-explanation">{{ rule.explanation }}</div>
          <div class="rule-code">
            <pre>{{ rule.mettaCode }}</pre>
          </div>
        </q-timeline-entry>
      </q-timeline>
    </q-card-section>
    
    <q-card-section v-if="decision.alternativeOptions && decision.alternativeOptions.length">
      <div class="text-subtitle2">Alternative Outcomes Considered</div>
      <q-list separator>
        <q-item
          v-for="(option, index) in decision.alternativeOptions"
          :key="index"
          clickable
          v-ripple
        >
          <q-item-section>
            <q-item-label>{{ option.result }}</q-item-label>
            <q-item-label caption>{{ option.explanation }}</q-item-label>
          </q-item-section>
          <q-item-section side>
            Confidence: {{ option.confidence }}%
          </q-item-section>
        </q-item>
      </q-list>
    </q-card-section>
    
    <q-card-actions align="right">
      <q-btn
        v-if="decision.canAppeal"
        flat
        color="primary"
        label="Appeal Decision"
        @click="$emit('appeal')"
      />
      <q-btn
        flat
        color="secondary"
        label="View Full Reasoning"
        @click="$emit('view-full')"
      />
    </q-card-actions>
  </q-card>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  decision: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['appeal', 'view-full'])

const formatDecisionResult = (result) => {
  if (result === 'approved') return 'Approved'
  if (result === 'rejected') return 'Rejected'
  if (result === 'pending') return 'Needs More Information'
  return result
}
</script>
```

## Implementation Timeline

### Week 1
- [ ] Create base MeTTa visualization components
- [ ] Set up data structure for MeTTa reasoning chains
- [ ] Implement basic styling for MeTTa components

### Week 2
- [ ] Integrate with backend MeTTa service
- [ ] Connect to real verification data
- [ ] Test with sample reasoning chains

### Week 3
- [ ] Add interactive visualizations
- [ ] Implement animation for reasoning steps
- [ ] Add user feedback mechanisms for MeTTa decisions

## Integration Points with Backend

The frontend will call these backend endpoints to retrieve MeTTa reasoning data:

- GET `/api/metta/reasoning/{contributionId}` - Get reasoning chain for a contribution
- GET `/api/metta/token-calculation/{contributionId}` - Get token award calculation
- GET `/api/metta/reputation/{userId}` - Get reputation score details

## Mock Data Structure

For development, we can use this mock data structure:

```javascript
// Example reasoning data structure
const mockReasoningData = {
  contributionId: "123",
  verified: true,
  confidence: 87,
  mettaProofHash: "0x1a2b3c4d5e6f7890",
  steps: [
    {
      type: "Evidence Analysis",
      explanation: "Analyzed uploaded GitHub repository with 15 commits",
      confidence: 92,
      result: "valid"
    },
    {
      type: "Skills Verification",
      explanation: "Python programming skills verified through code quality analysis",
      confidence: 89,
      result: "valid"
    },
    {
      type: "Impact Assessment",
      explanation: "Project has 12 stars and 5 forks indicating moderate impact",
      confidence: 78,
      result: "valid"
    }
  ],
  rules: [
    {
      name: "Evidence Authenticity",
      description: "Check if evidence is authentic and belongs to the user",
      satisfied: true,
      explanation: "GitHub commits match user's registered email",
      mettaCode: "(= (authentic-evidence $user $evidence) (matches-email $user $evidence))"
    },
    {
      name: "Skill Relevance",
      description: "Check if claimed skills match the contribution evidence",
      satisfied: true,
      explanation: "Python skills evident in code repository",
      mettaCode: "(= (skill-match $user $contribution) (and (skill $user python) (contains $contribution python)))"
    }
  ]
}
```

## Design Considerations

1. **Transparency** - All MeTTa decisions should be explainable to users
2. **Simplicity** - Complex reasoning chains should be presented in digestible formats
3. **Interactivity** - Users should be able to explore reasoning steps
4. **Educational** - Help users understand how the MeTTa AI works
5. **Feedback Loop** - Allow users to provide feedback on AI decisions

## Next Steps

1. Coordinate with backend team on MeTTa reasoning data formats
2. Create initial component prototypes for review
3. Test components with sample MeTTa reasoning data
4. Integrate into the contribution verification flow

This MeTTa integration plan will ensure users understand how autonomous decisions are made in the Nimo platform, providing transparency and building trust in the system.