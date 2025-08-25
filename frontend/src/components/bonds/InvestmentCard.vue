<template>
  <q-card class="investment-card">
    <q-card-section>
      <div class="row items-center no-wrap">
        <div class="col">
          <div class="text-h6 ellipsis">{{ investment.bond_title }}</div>
          <div class="text-caption">Invested on {{ formatDate(investment.created_at) }}</div>
        </div>
        <div class="col-auto">
          <q-avatar color="primary" text-color="white">
            <q-icon name="account_balance" />
          </q-avatar>
        </div>
      </div>
    </q-card-section>

    <q-separator />

    <q-card-section>
      <div class="row items-center">
        <div class="col">
          <div class="text-subtitle1">Investment Amount</div>
          <div class="text-h5 q-mt-sm">{{ investment.amount }} tokens</div>
        </div>
        <div class="col-auto">
          <q-btn flat round color="primary" icon="open_in_new" title="View Bond Details" />
        </div>
      </div>
    </q-card-section>

    <q-card-section v-if="bond">
      <div class="row items-center q-mb-sm">
        <div class="col">Funding Progress</div>
        <div class="col-auto">{{ bond.funding_percentage }}%</div>
      </div>
      <q-linear-progress
        :value="bond.funding_percentage / 100"
        size="10px"
        rounded
        :color="progressColor(bond.funding_percentage)"
      />
      
      <div class="row items-center q-mt-md q-mb-sm">
        <div class="col">Project Progress</div>
        <div class="col-auto">{{ bond.progress_percentage }}%</div>
      </div>
      <q-linear-progress
        :value="bond.progress_percentage / 100"
        size="10px"
        rounded
        color="green"
      />
      
      <div class="row q-mt-sm">
        <div class="col-12 text-caption text-grey">
          {{ bond.verified_milestones }} of {{ bond.milestone_count }} milestones completed
        </div>
      </div>
    </q-card-section>

    <q-card-actions align="right">
      <q-btn flat color="primary" label="View NFT Certificate" icon="verified" />
      <q-btn flat color="secondary" label="Share" icon="share" />
    </q-card-actions>
  </q-card>
</template>

<script>
import { computed } from 'vue'
import { date } from 'quasar'

export default {
  name: 'InvestmentCard',
  
  props: {
    investment: {
      type: Object,
      required: true
    }
  },
  
  setup(props) {
    // In a real app, we would fetch the bond details
    // For now, we'll use mock data
    const bond = computed(() => {
      // Mock bond data - this would come from API in real app
      if (props.investment.bond_id === 2) {
        return {
          funding_percentage: 75,
          progress_percentage: 50,
          verified_milestones: 2,
          milestone_count: 4
        }
      } else if (props.investment.bond_id === 3) {
        return {
          funding_percentage: 90,
          progress_percentage: 66,
          verified_milestones: 2,
          milestone_count: 3
        }
      }
      return null
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
      bond,
      formatDate,
      progressColor
    }
  }
}
</script>

<style lang="scss" scoped>
.investment-card {
  height: 100%;
  transition: box-shadow 0.3s;
  
  &:hover {
    box-shadow: 0 8px 12px rgba(0, 0, 0, 0.1);
  }
  
  .ellipsis {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
</style>