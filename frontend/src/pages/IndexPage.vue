<template>
  <q-page class="page-container">
    <div class="row q-col-gutter-md">
      <!-- Welcome card -->
      <div class="col-12">
        <q-card class="welcome-card">
          <q-card-section class="bg-primary text-white">
            <div class="text-h5">Welcome to Nimo</div>
            <div class="text-subtitle2">Decentralized Youth Identity & Proof of Contribution Network on Base</div>
          </q-card-section>
          <q-card-section>
            <p>Build your NFT identity, earn reputation tokens for contributions, and access global opportunities through Base network.</p>
            
            <!-- Wallet Connection -->
            <div class="wallet-section q-mb-md">
              <WalletConnect />
            </div>

            <!-- Network Status -->
            <div v-if="walletStore.isConnected" class="network-status q-mb-md">
              <q-chip
                :color="walletStore.isOnCorrectNetwork ? 'positive' : 'warning'"
                text-color="white"
                icon="lan"
                class="q-mr-sm"
              >
                {{ walletStore.networkName }}
              </q-chip>
              
              <q-chip
                color="info"
                text-color="white"
                icon="account_balance"
              >
                {{ formattedBalance }} ETH
              </q-chip>
            </div>

            <q-btn 
              v-if="walletStore.isConnected && walletStore.isOnCorrectNetwork"
              color="secondary" 
              label="Create Your Identity" 
              to="/profile"
              icon="person_add"
            />
            <div v-else-if="!walletStore.isConnected" class="text-caption q-mt-sm">
              Connect your wallet to get started
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Stats row -->
      <div class="col-12 col-md-4">
        <q-card class="dashboard-card">
          <q-card-section>
            <div class="text-h6">Your Contributions</div>
            <div class="text-h3 text-primary">{{ contributionCount }}</div>
            <div class="text-caption">Total contributions recorded</div>
          </q-card-section>
          <q-card-actions>
            <q-btn flat color="primary" label="View All" to="/contributions" />
          </q-card-actions>
        </q-card>
      </div>
      
      <div class="col-12 col-md-4">
        <q-card class="dashboard-card">
          <q-card-section>
            <div class="text-h6">Reputation Tokens</div>
            <div class="text-h3 text-primary">{{ tokenBalance }}</div>
            <div class="text-caption">Current token balance</div>
          </q-card-section>
          <q-card-actions>
            <q-btn flat color="primary" label="View Tokens" to="/tokens" />
          </q-card-actions>
        </q-card>
      </div>
      
      <div class="col-12 col-md-4">
        <q-card class="dashboard-card">
          <q-card-section>
            <div class="text-h6">Verifications</div>
            <div class="text-h3 text-primary">{{ verificationCount }}</div>
            <div class="text-caption">Contributions verified</div>
          </q-card-section>
          <q-card-actions>
            <q-btn flat color="primary" label="View Details" to="/contributions" />
          </q-card-actions>
        </q-card>
      </div>

      <!-- Recent activity -->
      <div class="col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6">Recent Activity</div>
          </q-card-section>
          <q-list separator>
            <q-item v-for="activity in recentActivity" :key="activity.id">
              <q-item-section avatar>
                <q-icon :name="activity.icon" :color="activity.color" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ activity.title }}</q-item-label>
                <q-item-label caption>{{ activity.date }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item v-if="recentActivity.length === 0">
              <q-item-section>
                <q-item-label class="text-center text-grey">No recent activity</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useWalletStore } from 'src/stores/wallet'
import WalletConnect from 'src/components/WalletConnect.vue'

const walletStore = useWalletStore()

// Mock data for demonstration
const contributionCount = ref(5)
const tokenBalance = ref(250)
const verificationCount = ref(3)

const recentActivity = ref([
  {
    id: 1,
    title: 'Contribution "Community Workshop" verified by Tech Community',
    date: 'Today, 2:30 PM',
    icon: 'check_circle',
    color: 'positive'
  },
  {
    id: 2,
    title: 'You received 50 reputation tokens',
    date: 'Today, 2:30 PM',
    icon: 'token',
    color: 'primary'
  },
  {
    id: 3,
    title: 'New contribution "Open Source Project" added',
    date: 'Yesterday, 10:15 AM',
    icon: 'work',
    color: 'info'
  }
])

const formattedBalance = computed(() => {
  const balance = parseFloat(walletStore.balance)
  return balance.toFixed(4)
})
</script>

<style lang="scss" scoped>
.welcome-card {
  background: linear-gradient(135deg, rgba(255,255,255,1) 0%, rgba(240,242,245,1) 100%);
}

.dashboard-card {
  height: 100%;
}
</style>