<template>
  <div class="wallet-connect">
    <!-- Wallet Connection Button -->
    <q-btn
      v-if="!isConnected"
      @click="handleConnect"
      :loading="isConnecting"
      color="primary"
      icon="account_balance_wallet"
      label="Connect Wallet"
      class="wallet-connect-btn"
      unelevated
    />

    <!-- Wallet Info Display -->
    <div v-else class="wallet-info">
      <q-chip
        :color="isOnCorrectNetwork ? 'positive' : 'negative'"
        text-color="white"
        icon="account_balance_wallet"
        class="wallet-chip"
      >
        {{ formattedAddress }}
      </q-chip>

      <q-btn
        flat
        round
        icon="more_vert"
        @click="showWalletMenu = true"
        class="wallet-menu-btn"
      />

      <!-- Wallet Menu -->
      <q-menu v-model="showWalletMenu" anchor="bottom right" self="top right">
        <q-list style="min-width: 200px">
          <!-- Network Info -->
          <q-item>
            <q-item-section>
              <q-item-label class="text-caption text-grey-6">Network</q-item-label>
              <q-item-label>{{ networkName }}</q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-icon
                :name="isOnCorrectNetwork ? 'check_circle' : 'error'"
                :color="isOnCorrectNetwork ? 'positive' : 'negative'"
              />
            </q-item-section>
          </q-item>

          <!-- Balance -->
          <q-item>
            <q-item-section>
              <q-item-label class="text-caption text-grey-6">Balance</q-item-label>
              <q-item-label>{{ formattedBalance }} ETH</q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-btn
                flat
                round
                dense
                icon="refresh"
                @click="handleRefreshBalance"
                :loading="refreshingBalance"
              />
            </q-item-section>
          </q-item>

          <q-separator />

          <!-- Switch Network -->
          <q-item
            v-if="!isOnCorrectNetwork"
            clickable
            @click="handleSwitchNetwork"
          >
            <q-item-section avatar>
              <q-icon name="swap_horiz" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Switch to Base</q-item-label>
            </q-item-section>
          </q-item>

          <!-- Copy Address -->
          <q-item clickable @click="copyAddress">
            <q-item-section avatar>
              <q-icon name="content_copy" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Copy Address</q-item-label>
            </q-item-section>
          </q-item>

          <!-- View on Explorer -->
          <q-item clickable @click="viewOnExplorer">
            <q-item-section avatar>
              <q-icon name="open_in_new" />
            </q-item-section>
            <q-item-section>
              <q-item-label>View on BaseScan</q-item-label>
            </q-item-section>
          </q-item>

          <q-separator />

          <!-- Disconnect -->
          <q-item clickable @click="handleDisconnect" class="text-negative">
            <q-item-section avatar>
              <q-icon name="logout" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Disconnect</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-menu>
    </div>

    <!-- Error Dialog -->
    <q-dialog v-model="showErrorDialog">
      <q-card class="error-card">
        <q-card-section class="row items-center">
          <q-icon name="error" color="negative" size="md" class="q-mr-sm" />
          <span class="text-h6">Connection Error</span>
        </q-card-section>

        <q-card-section>
          <p>{{ error }}</p>
          <div v-if="!walletStore.isMetaMaskInstalled()" class="q-mt-md">
            <p class="text-caption">
              Don't have MetaMask? Download it here:
            </p>
            <q-btn
              color="primary"
              label="Install MetaMask"
              icon="download"
              @click="openMetaMaskDownload"
              unelevated
              class="q-mt-sm"
            />
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Close" @click="showErrorDialog = false" />
          <q-btn
            v-if="walletStore.isMetaMaskInstalled()"
            color="primary"
            label="Try Again"
            @click="retryConnection"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Network Warning -->
    <q-banner
      v-if="isConnected && !isOnCorrectNetwork"
      class="bg-warning text-dark q-mt-sm"
      rounded
    >
      <template v-slot:avatar>
        <q-icon name="warning" />
      </template>
      <div>
        Wrong network detected. Please switch to Base network.
        <q-btn
          flat
          label="Switch Network"
          @click="handleSwitchNetwork"
          class="q-ml-sm"
        />
      </div>
    </q-banner>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useWalletStore } from 'src/stores/wallet'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const walletStore = useWalletStore()

// Local state
const showWalletMenu = ref(false)
const showErrorDialog = ref(false)
const refreshingBalance = ref(false)

// Computed properties
const isConnected = computed(() => walletStore.isConnected)
const isConnecting = computed(() => walletStore.isConnecting)
const isOnCorrectNetwork = computed(() => walletStore.isOnCorrectNetwork)
const formattedAddress = computed(() => walletStore.formattedAddress)
const networkName = computed(() => walletStore.networkName)
const error = computed(() => walletStore.error)
const formattedBalance = computed(() => {
  const balance = parseFloat(walletStore.balance)
  return balance.toFixed(4)
})

// Methods
const handleConnect = async () => {
  const success = await walletStore.connectWallet()
  if (!success && walletStore.error) {
    showErrorDialog.value = true
  }
}

const handleDisconnect = () => {
  walletStore.disconnectWallet()
  showWalletMenu.value = false
  $q.notify({
    type: 'info',
    message: 'Wallet disconnected',
    position: 'top-right'
  })
}

const handleSwitchNetwork = async () => {
  const success = await walletStore.switchToBaseNetwork()
  if (success) {
    $q.notify({
      type: 'positive',
      message: 'Successfully switched to Base network',
      position: 'top-right'
    })
  }
  showWalletMenu.value = false
}

const handleRefreshBalance = async () => {
  refreshingBalance.value = true
  await walletStore.updateBalance()
  refreshingBalance.value = false
  $q.notify({
    type: 'info',
    message: 'Balance updated',
    position: 'top-right'
  })
}

const copyAddress = async () => {
  if (navigator.clipboard && walletStore.account) {
    try {
      await navigator.clipboard.writeText(walletStore.account)
      $q.notify({
        type: 'positive',
        message: 'Address copied to clipboard',
        position: 'top-right'
      })
    } catch (err) {
      $q.notify({
        type: 'negative',
        message: 'Failed to copy address',
        position: 'top-right'
      })
    }
  }
  showWalletMenu.value = false
}

const viewOnExplorer = () => {
  if (walletStore.account && walletStore.chainId) {
    const network = walletStore.BASE_NETWORKS[walletStore.chainId]
    const explorerUrl = network?.blockExplorerUrls?.[0]
    if (explorerUrl) {
      window.open(`${explorerUrl}/address/${walletStore.account}`, '_blank')
    }
  }
  showWalletMenu.value = false
}

const openMetaMaskDownload = () => {
  window.open('https://metamask.io/download/', '_blank')
  showErrorDialog.value = false
}

const retryConnection = () => {
  showErrorDialog.value = false
  walletStore.clearError()
  handleConnect()
}

// Watch for errors
watch(error, (newError) => {
  if (newError && !isConnecting.value) {
    showErrorDialog.value = true
  }
})

// Lifecycle
onMounted(() => {
  walletStore.setupEventListeners()
  walletStore.autoConnect()
})

onUnmounted(() => {
  walletStore.removeEventListeners()
})
</script>

<style lang="scss" scoped>
.wallet-connect {
  display: flex;
  align-items: center;
  gap: 8px;
}

.wallet-connect-btn {
  min-width: 140px;
}

.wallet-info {
  display: flex;
  align-items: center;
  gap: 4px;
}

.wallet-chip {
  cursor: pointer;
  transition: opacity 0.2s;

  &:hover {
    opacity: 0.8;
  }
}

.wallet-menu-btn {
  opacity: 0.7;
  transition: opacity 0.2s;

  &:hover {
    opacity: 1;
  }
}

.error-card {
  min-width: 300px;
  max-width: 400px;
}
</style>