<template>
  <q-page class="page-container">
    <div class="row q-col-gutter-md">
      <div class="col-12 col-md-8">
        <q-card>
          <q-card-section class="bg-primary text-white">
            <div class="text-h5">Reputation Tokens</div>
            <div class="text-subtitle2">Your earned reputation on the Nimo platform</div>
          </q-card-section>
          
          <q-card-section class="row items-center">
            <div class="col-12 col-md-6 text-center q-pa-md">
              <div class="text-h3 text-primary q-mb-sm">250</div>
              <div class="text-subtitle1">Available Tokens</div>
              <q-btn color="primary" label="View History" class="q-mt-md" />
            </div>
            <div class="col-12 col-md-6">
              <q-list bordered separator>
                <q-item>
                  <q-item-section>
                    <q-item-label>Community Impact</q-item-label>
                    <q-item-label caption>Contributions to local initiatives</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <div class="text-weight-bold">120</div>
                  </q-item-section>
                </q-item>
                
                <q-item>
                  <q-item-section>
                    <q-item-label>Skill Development</q-item-label>
                    <q-item-label caption>Learning and skill verification</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <div class="text-weight-bold">85</div>
                  </q-item-section>
                </q-item>
                
                <q-item>
                  <q-item-section>
                    <q-item-label>Engagement</q-item-label>
                    <q-item-label caption>Platform participation</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <div class="text-weight-bold">45</div>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </q-card-section>
        </q-card>
        
        <q-card class="q-mt-md">
          <q-card-section class="bg-primary text-white">
            <div class="text-h5">Recent Transactions</div>
          </q-card-section>
          
          <q-list bordered separator>
            <q-item v-for="transaction in transactions" :key="transaction.id">
              <q-item-section avatar>
                <q-icon :name="transactionIcon(transaction.type)" :color="transactionColor(transaction.type)" />
              </q-item-section>
              
              <q-item-section>
                <q-item-label>{{ transaction.description }}</q-item-label>
                <q-item-label caption>{{ formatDate(transaction.timestamp) }}</q-item-label>
              </q-item-section>
              
              <q-item-section side>
                <div :class="transaction.amount > 0 ? 'text-positive' : 'text-negative'">
                  {{ transaction.amount > 0 ? '+' : '' }}{{ transaction.amount }}
                </div>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div>
      
      <div class="col-12 col-md-4">
        <q-card>
          <q-card-section class="bg-primary text-white">
            <div class="text-h5">Usage Options</div>
          </q-card-section>
          
          <q-list bordered separator>
            <q-item clickable to="/bonds">
              <q-item-section avatar>
                <q-icon name="account_balance" color="primary" />
              </q-item-section>
              
              <q-item-section>
                <q-item-label>Invest in Impact Bonds</q-item-label>
                <q-item-label caption>Support community initiatives</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item clickable>
              <q-item-section avatar>
                <q-icon name="school" color="primary" />
              </q-item-section>
              
              <q-item-section>
                <q-item-label>Educational Opportunities</q-item-label>
                <q-item-label caption>Unlock courses and certifications</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item clickable>
              <q-item-section avatar>
                <q-icon name="work" color="primary" />
              </q-item-section>
              
              <q-item-section>
                <q-item-label>Job Marketplace</q-item-label>
                <q-item-label caption>Access exclusive opportunities</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
        
        <q-card class="q-mt-md">
          <q-card-section class="bg-primary text-white">
            <div class="text-h5">Earn More Tokens</div>
          </q-card-section>
          
          <q-list bordered separator>
            <q-item clickable to="/contributions">
              <q-item-section avatar>
                <q-icon name="add_task" color="green" />
              </q-item-section>
              
              <q-item-section>
                <q-item-label>Submit New Contribution</q-item-label>
                <q-item-label caption>Document your real-world impact</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item clickable>
              <q-item-section avatar>
                <q-icon name="verified" color="green" />
              </q-item-section>
              
              <q-item-section>
                <q-item-label>Verify Others' Contributions</q-item-label>
                <q-item-label caption>Help maintain network integrity</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item clickable>
              <q-item-section avatar>
                <q-icon name="workspace_premium" color="green" />
              </q-item-section>
              
              <q-item-section>
                <q-item-label>Complete Skills Assessment</q-item-label>
                <q-item-label caption>Validate your knowledge</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script>
import { ref } from 'vue'
import { date } from 'quasar'

export default {
  name: 'TokensPage',
  
  setup() {
    const transactions = ref([
      {
        id: 1,
        type: 'earned',
        description: 'Community Clean-up Contribution',
        amount: 25,
        timestamp: '2025-08-15T14:30:00'
      },
      {
        id: 2,
        type: 'invested',
        description: 'Invested in "Coding Bootcamp for Underprivileged Youth"',
        amount: -1000,
        timestamp: '2025-08-12T16:30:00'
      },
      {
        id: 3,
        type: 'earned',
        description: 'Python Programming Skill Verification',
        amount: 50,
        timestamp: '2025-08-10T11:15:00'
      },
      {
        id: 4,
        type: 'invested',
        description: 'Invested in "Women\'s Entrepreneurship Network"',
        amount: -500,
        timestamp: '2025-08-08T14:15:00'
      },
      {
        id: 5,
        type: 'earned',
        description: 'Mentorship Session Contribution',
        amount: 35,
        timestamp: '2025-08-05T10:00:00'
      }
    ])
    
    function formatDate(dateString) {
      return date.formatDate(dateString, 'MMM D, YYYY - h:mm A')
    }
    
    function transactionIcon(type) {
      switch(type) {
        case 'earned':
          return 'add_circle'
        case 'invested':
          return 'account_balance'
        default:
          return 'swap_horiz'
      }
    }
    
    function transactionColor(type) {
      switch(type) {
        case 'earned':
          return 'positive'
        case 'invested':
          return 'primary'
        default:
          return 'grey'
      }
    }
    
    return {
      transactions,
      formatDate,
      transactionIcon,
      transactionColor
    }
  }
}
</script>

<style lang="scss" scoped>
.page-container {
  padding: 16px;
  max-width: 1200px;
  margin: 0 auto;
}
</style>