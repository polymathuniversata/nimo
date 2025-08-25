<template>
  <q-card class="bond-card">
    <q-img
      :src="bond.image_url || 'https://placehold.co/600x200/e0e0e0/a0a0a0?text=Impact+Bond'"
      height="200px"
    >
      <div class="absolute-bottom text-subtitle2 text-right">
        <q-badge :color="causeBadgeColor">
          {{ causeLabel }}
        </q-badge>
      </div>
    </q-img>

    <q-card-section>
      <div class="text-h6 ellipsis-2-lines">{{ bond.title }}</div>
      <div class="text-subtitle2">
        Created by {{ bond.creator_name }} · {{ formatDate(bond.created_at) }}
      </div>
    </q-card-section>

    <q-card-section>
      <div class="text-body2 ellipsis-3-lines">{{ bond.description }}</div>
    </q-card-section>

    <q-card-section>
      <div class="row items-center">
        <div class="col">Funding Progress</div>
        <div class="col-auto">{{ bond.funding_percentage }}%</div>
      </div>
      <q-linear-progress
        :value="bond.funding_percentage / 100"
        size="15px"
        rounded
        class="q-mt-sm"
        :color="progressColor(bond.funding_percentage)"
      />
      <div class="row justify-between text-subtitle2 q-mt-xs">
        <div>{{ bond.total_investment }} tokens raised</div>
        <div>{{ bond.value }} goal</div>
      </div>
    </q-card-section>

    <q-card-section v-if="bond.milestone_count > 0">
      <div class="row items-center">
        <div class="col">Project Progress</div>
        <div class="col-auto">{{ bond.progress_percentage }}%</div>
      </div>
      <q-linear-progress
        :value="bond.progress_percentage / 100"
        size="15px"
        rounded
        class="q-mt-sm"
        color="green"
      />
      <div class="row justify-between text-subtitle2 q-mt-xs">
        <div>{{ bond.verified_milestones }} verified</div>
        <div>{{ bond.milestone_count }} milestones</div>
      </div>
    </q-card-section>

    <q-card-actions align="right">
      <template v-if="isOwner">
        <q-btn flat color="primary" icon="add_task" label="Add Milestone" @click="$emit('add-milestone', bond)" />
      </template>
      <template v-else>
        <q-btn flat color="primary" icon="remove_red_eye" label="View Details" />
        <q-btn color="primary" icon="account_balance_wallet" label="Invest" @click="$emit('invest', bond)" />
      </template>
    </q-card-actions>
  </q-card>
</template>

<script>
import { computed } from 'vue'
import { date } from 'quasar'

export default {
  name: 'BondCard',
  
  props: {
    bond: {
      type: Object,
      required: true
    },
    isOwner: {
      type: Boolean,
      default: false
    }
  },
  
  setup(props) {
    const causeLabel = computed(() => {
      const causeMap = {
        'climate': 'Climate Action',
        'education': 'Education',
        'economic-empowerment': 'Economic Empowerment',
        'health': 'Health',
        'technology': 'Technology',
        'agriculture': 'Agriculture',
        'arts': 'Arts & Culture'
      }
      return causeMap[props.bond.cause] || props.bond.cause
    })
    
    const causeBadgeColor = computed(() => {
      const colorMap = {
        'climate': 'green',
        'education': 'blue',
        'economic-empowerment': 'purple',
        'health': 'red',
        'technology': 'deep-purple',
        'agriculture': 'lime',
        'arts': 'pink'
      }
      return colorMap[props.bond.cause] || 'grey'
    })
    
    function formatDate(dateString) {
      return date.formatDate(dateString, 'MMM D, YYYY')
    }
    
    function progressColor(percentage) {
      if (percentage < 25) return 'red'
      if (percentage < 50) return 'orange'
      if (percentage < 75) return 'lime'
      return 'green'
    }
    
    return {
      causeLabel,
      causeBadgeColor,
      formatDate,
      progressColor
    }
  }
}
</script>

<style lang="scss" scoped>
.bond-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s;
  
  &:hover {
    transform: translateY(-5px);
  }
  
  .ellipsis-2-lines {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .ellipsis-3-lines {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}
</style>