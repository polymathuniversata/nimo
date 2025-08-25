<template>
  <div class="landing-page">
    <!-- Navigation -->
    <q-header class="navbar" reveal>
      <q-toolbar class="navbar-content">
        <router-link to="/" class="logo">
          <q-toolbar-title>Nimo</q-toolbar-title>
        </router-link>
        
        <q-space />
        
        <div class="nav-links desktop-only">
          <q-btn flat @click="scrollTo('features')">Features</q-btn>
          <q-btn flat @click="scrollTo('how-it-works')">How It Works</q-btn>
          <q-btn flat @click="scrollTo('about')">About</q-btn>
          <q-btn flat @click="scrollTo('contact')">Contact</q-btn>
        </div>
        
        <q-btn
          @click="handleConnectWallet"
          :loading="walletStore.isConnecting"
          color="primary"
          :label="walletStore.isConnected ? 'Connected' : 'Connect Wallet'"
          :icon="walletStore.isConnected ? 'check_circle' : 'account_balance_wallet'"
          unelevated
          rounded
          class="q-ml-md"
        />
        
        <q-btn
          flat
          round
          icon="menu"
          class="mobile-only q-ml-sm"
          @click="drawer = !drawer"
        />
      </q-toolbar>
    </q-header>

    <!-- Mobile Navigation Drawer -->
    <q-drawer
      v-model="drawer"
      side="right"
      overlay
      behavior="mobile"
      class="mobile-only"
    >
      <q-list>
        <q-item clickable @click="scrollTo('features')">
          <q-item-section>Features</q-item-section>
        </q-item>
        <q-item clickable @click="scrollTo('how-it-works')">
          <q-item-section>How It Works</q-item-section>
        </q-item>
        <q-item clickable @click="scrollTo('about')">
          <q-item-section>About</q-item-section>
        </q-item>
        <q-item clickable @click="scrollTo('contact')">
          <q-item-section>Contact</q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <div class="row items-center q-col-gutter-xl">
          <div class="col-12 col-md-6">
            <div class="hero-text">
              <h1 class="hero-title animate-fade-in">
                Build Your Digital Identity on Base
              </h1>
              <p class="hero-subtitle animate-fade-in animate-delay-1">
                Nimo empowers young creators to build verified digital identities, earn reputation tokens for contributions, and access global opportunities through the Base network.
              </p>
              <div class="cta-buttons animate-fade-in animate-delay-2">
                <q-btn
                  @click="handleGetStarted"
                  color="white"
                  text-color="primary"
                  size="lg"
                  unelevated
                  rounded
                  icon="rocket_launch"
                  label="Get Started"
                  class="q-mr-md q-mb-sm"
                  :loading="walletStore.isConnecting"
                />
                <q-btn
                  @click="scrollTo('features')"
                  outline
                  color="white"
                  size="lg"
                  rounded
                  icon="play_arrow"
                  label="Learn More"
                  class="q-mb-sm"
                />
              </div>
            </div>
          </div>
          <div class="col-12 col-md-6">
            <div class="hero-visual animate-fade-in animate-delay-3">
              <q-card class="hero-card">
                <q-card-section class="identity-preview">
                  <div class="profile-avatar">
                    <q-icon name="person" size="2rem" />
                  </div>
                  <div class="text-center">
                    <div class="text-h6 text-dark">Digital Identity NFT</div>
                    <div class="text-caption text-grey-6 q-mt-xs">
                      Verified • Base Network
                    </div>
                  </div>
                </q-card-section>
                <q-separator />
                <q-card-section class="row justify-around text-white">
                  <div class="text-center">
                    <div class="text-caption">Contributions</div>
                    <div class="text-h6">12</div>
                  </div>
                  <div class="text-center">
                    <div class="text-caption">Reputation</div>
                    <div class="text-h6">850</div>
                  </div>
                  <div class="text-center">
                    <div class="text-caption">Verifications</div>
                    <div class="text-h6">8</div>
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="features">
      <div class="container">
        <div class="section-header text-center q-mb-xl">
          <h2 class="section-title">Powerful Features for Digital Creators</h2>
          <p class="section-subtitle">
            Everything you need to build, verify, and monetize your digital identity on the blockchain
          </p>
        </div>
        
        <div class="row q-col-gutter-lg">
          <div class="col-12 col-md-4" v-for="feature in features" :key="feature.title">
            <q-card class="feature-card full-height" flat bordered>
              <q-card-section class="text-center">
                <div class="feature-icon q-mb-md">
                  <q-icon :name="feature.icon" size="3rem" />
                </div>
                <h3 class="text-h6 q-mb-sm">{{ feature.title }}</h3>
                <p class="text-body2 text-grey-7">{{ feature.description }}</p>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section id="how-it-works" class="how-it-works">
      <div class="container">
        <div class="section-header text-center q-mb-xl">
          <h2 class="section-title">How Nimo Works</h2>
          <p class="section-subtitle">
            Get started with your digital identity in four simple steps
          </p>
        </div>
        
        <div class="row q-col-gutter-lg">
          <div class="col-12 col-sm-6 col-lg-3" v-for="(step, index) in steps" :key="step.title">
            <div class="step-card text-center">
              <div class="step-number q-mb-md">{{ index + 1 }}</div>
              <h3 class="text-h6 q-mb-sm">{{ step.title }}</h3>
              <p class="text-body2 text-grey-7">{{ step.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="stats">
      <div class="container">
        <div class="row q-col-gutter-lg text-center text-white">
          <div class="col-12 col-sm-6 col-lg-3" v-for="stat in stats" :key="stat.label">
            <div class="stat-item">
              <h3 class="stat-number">{{ stat.value }}</h3>
              <p class="stat-label">{{ stat.label }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="container text-center">
        <h2 class="section-title q-mb-md">Ready to Build Your Digital Future?</h2>
        <p class="section-subtitle q-mb-lg">
          Join thousands of creators who are already building their reputation on the Base network
        </p>
        <div class="cta-buttons">
          <q-btn
            @click="handleConnectWallet"
            color="primary"
            size="lg"
            unelevated
            rounded
            icon="account_balance_wallet"
            label="Connect Wallet & Start"
            class="q-mr-md q-mb-sm"
            :loading="walletStore.isConnecting"
          />
          <q-btn
            outline
            color="primary"
            size="lg"
            rounded
            icon="description"
            label="Read Documentation"
            class="q-mb-sm"
          />
        </div>
      </div>
    </section>

    <!-- Footer -->
    <q-footer class="footer">
      <div class="container">
        <div class="row q-col-gutter-lg q-mb-lg">
          <div class="col-12 col-md-3">
            <div class="footer-section">
              <h3 class="text-h6 text-secondary q-mb-md">Nimo</h3>
              <p class="text-body2 text-grey-4">
                Building the future of digital identity for young creators on the Base network.
              </p>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="footer-section">
              <h3 class="text-subtitle1 text-secondary q-mb-md">Platform</h3>
              <div class="footer-links">
                <a href="#" class="footer-link">Features</a>
                <a href="#" class="footer-link">How It Works</a>
                <a href="#" class="footer-link">Statistics</a>
                <a href="#" class="footer-link">Roadmap</a>
              </div>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="footer-section">
              <h3 class="text-subtitle1 text-secondary q-mb-md">Resources</h3>
              <div class="footer-links">
                <a href="#" class="footer-link">Documentation</a>
                <a href="#" class="footer-link">API Reference</a>
                <a href="#" class="footer-link">Smart Contracts</a>
                <a href="#" class="footer-link">GitHub</a>
              </div>
            </div>
          </div>
          <div class="col-12 col-md-3">
            <div class="footer-section">
              <h3 class="text-subtitle1 text-secondary q-mb-md">Community</h3>
              <div class="footer-links">
                <a href="#" class="footer-link">Discord</a>
                <a href="#" class="footer-link">Twitter</a>
                <a href="#" class="footer-link">Telegram</a>
                <a href="#" class="footer-link">Blog</a>
              </div>
            </div>
          </div>
        </div>
        
        <q-separator color="grey-8" />
        
        <div class="footer-bottom text-center q-pt-lg">
          <p class="text-body2 text-grey-5">
            &copy; 2024 Nimo Platform. Built on Base Network.
          </p>
        </div>
      </div>
    </q-footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useWalletStore } from 'src/stores/wallet'

const $q = useQuasar()
const router = useRouter()
const walletStore = useWalletStore()

// Reactive state
const drawer = ref(false)

// Features data
const features = ref([
  {
    title: 'NFT Identity',
    description: 'Create a unique, verifiable digital identity as an NFT on the Base network. Your identity, your control.',
    icon: 'verified_user'
  },
  {
    title: 'Reputation System',
    description: 'Earn reputation tokens for your contributions and achievements. Build trust in the decentralized economy.',
    icon: 'stars'
  },
  {
    title: 'Community Verification',
    description: 'Get your skills and contributions verified by trusted community members and organizations.',
    icon: 'group'
  },
  {
    title: 'Base Network',
    description: 'Built on Base for fast, cheap transactions. Low fees mean more value for your contributions.',
    icon: 'account_balance'
  },
  {
    title: 'Opportunity Access',
    description: 'Use your verified identity to access jobs, grants, and opportunities in the Web3 ecosystem.',
    icon: 'work'
  },
  {
    title: 'Portfolio Growth',
    description: 'Track your progress and showcase your achievements to potential collaborators and employers.',
    icon: 'trending_up'
  }
])

// Steps data
const steps = ref([
  {
    title: 'Connect Your Wallet',
    description: 'Connect your MetaMask wallet and switch to the Base network to get started with Nimo.'
  },
  {
    title: 'Create Your Identity',
    description: 'Mint your unique digital identity NFT and start building your reputation profile.'
  },
  {
    title: 'Start Contributing',
    description: 'Add your contributions, get verified by the community, and earn reputation tokens.'
  },
  {
    title: 'Access Opportunities',
    description: 'Use your verified identity to unlock jobs, grants, and collaboration opportunities.'
  }
])

// Stats data
const stats = ref([
  { value: '1,200+', label: 'Active Creators' },
  { value: '5,400+', label: 'Verified Contributions' },
  { value: '850K', label: 'Reputation Tokens Earned' },
  { value: '320+', label: 'Opportunities Unlocked' }
])

// Methods
const handleConnectWallet = async () => {
  if (!walletStore.isConnected) {
    const success = await walletStore.connectWallet()
    if (success) {
      $q.notify({
        type: 'positive',
        message: 'Wallet connected! Redirecting to dashboard...',
        position: 'top-right',
        icon: 'check_circle'
      })
      
      // Redirect to dashboard after successful connection
      setTimeout(() => {
        router.push('/dashboard')
      }, 1500)
    }
  } else {
    // Already connected, go to dashboard
    router.push('/dashboard')
  }
}

const handleGetStarted = async () => {
  if (!walletStore.isConnected) {
    await handleConnectWallet()
  } else {
    router.push('/dashboard')
  }
}

const scrollTo = (elementId) => {
  drawer.value = false // Close mobile drawer
  const element = document.getElementById(elementId)
  if (element) {
    element.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    })
  }
}

// Lifecycle
onMounted(() => {
  // Setup wallet event listeners
  if (typeof window !== 'undefined') {
    walletStore.setupEventListeners()
  }
})
</script>

<style lang="scss" scoped>
.landing-page {
  min-height: 100vh;
}

// Navigation
.navbar {
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #e2e8f0;
}

.navbar-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.logo {
  text-decoration: none;
  color: inherit;
}

.nav-links {
  .q-btn {
    margin: 0 0.5rem;
    font-weight: 500;
  }
}

.desktop-only {
  @media (max-width: 768px) {
    display: none !important;
  }
}

.mobile-only {
  @media (min-width: 769px) {
    display: none !important;
  }
}

// Hero Section
.hero {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  padding: 2rem;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
    opacity: 0.3;
  }
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  z-index: 1;
  position: relative;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1.5rem;
  line-height: 1.2;
  
  @media (max-width: 768px) {
    font-size: 2.5rem;
  }
}

.hero-subtitle {
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2rem;
  line-height: 1.6;
}

.cta-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: stretch;
  }
}

// Hero Visual
.hero-visual {
  display: flex;
  justify-content: center;
  align-items: center;
}

.hero-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  max-width: 400px;
  width: 100%;
}

.identity-preview {
  background: white;
  border-radius: 15px;
  padding: 1.5rem;
}

.profile-avatar {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 50%;
  margin: 0 auto 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

// Sections
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.features,
.how-it-works,
.cta-section {
  padding: 6rem 1rem;
}

.features {
  background: #f8fafc;
}

.stats {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 4rem 1rem;
}

.section-header {
  margin-bottom: 4rem;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  
  @media (max-width: 768px) {
    font-size: 2rem;
  }
}

.section-subtitle {
  font-size: 1.25rem;
  color: #64748b;
  max-width: 600px;
  margin: 0 auto;
}

// Feature Cards
.feature-card {
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    transform: scaleX(0);
    transition: transform 0.3s ease;
  }

  &:hover {
    transform: translateY(-5px);
    
    &::before {
      transform: scaleX(1);
    }
  }
}

.feature-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

// Steps
.step-card {
  padding: 1rem;
}

.step-number {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 auto;
}

// Stats
.stat-item {
  padding: 1rem;
}

.stat-number {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 1.1rem;
  opacity: 0.9;
}

// Footer
.footer {
  background: #1a1a2e !important;
  color: white;
  padding: 3rem 1rem 1rem;
}

.footer-section {
  h3 {
    margin-bottom: 1rem;
  }
}

.footer-links {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.footer-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: color 0.3s ease;

  &:hover {
    color: #26a69a;
  }
}

.footer-bottom {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

// Animations
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeInUp 0.6s ease forwards;
}

.animate-delay-1 { animation-delay: 0.1s; }
.animate-delay-2 { animation-delay: 0.2s; }
.animate-delay-3 { animation-delay: 0.3s; }
</style>