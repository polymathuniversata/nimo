<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title>
          Nimo Platform
        </q-toolbar-title>

        <q-btn-dropdown flat dense icon="person" class="q-mr-sm">
          <q-list>
            <q-item clickable v-close-popup to="/profile">
              <q-item-section>
                <q-item-label>Profile</q-item-label>
              </q-item-section>
            </q-item>
            <q-item clickable v-close-popup @click="logout">
              <q-item-section>
                <q-item-label>Logout</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      bordered
      :width="280"
      show-if-above
      class="bg-grey-1"
    >
      <q-list>
        <q-item-label header>Navigation</q-item-label>
        
        <q-item clickable to="/" exact>
          <q-item-section avatar>
            <q-icon name="home" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Dashboard</q-item-label>
          </q-item-section>
        </q-item>

        <q-item clickable to="/profile">
          <q-item-section avatar>
            <q-icon name="person" />
          </q-item-section>
          <q-item-section>
            <q-item-label>My Profile</q-item-label>
          </q-item-section>
        </q-item>

        <q-item clickable to="/contributions">
          <q-item-section avatar>
            <q-icon name="work" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Contributions</q-item-label>
          </q-item-section>
        </q-item>

        <q-item clickable to="/tokens">
          <q-item-section avatar>
            <q-icon name="token" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Reputation Tokens</q-item-label>
          </q-item-section>
        </q-item>

        <q-item clickable to="/bonds">
          <q-item-section avatar>
            <q-icon name="account_balance" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Impact Bonds</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>

    <q-footer elevated class="bg-grey-8 text-white">
      <q-toolbar>
        <q-toolbar-title>
          <div class="text-caption">
            Nimo - Decentralized Youth Identity & Proof of Contribution Network &copy; 2025
          </div>
        </q-toolbar-title>
      </q-toolbar>
    </q-footer>
  </q-layout>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { authService, userService } from '../services'

export default {
  name: 'MainLayout',

  setup () {
    const leftDrawerOpen = ref(false)
    const router = useRouter()
    const $q = useQuasar()
    const user = ref({
      name: 'User',
      avatar: null
    })
    
    onMounted(async () => {
      if (authService.isAuthenticated()) {
        try {
          const response = await userService.getUserProfile()
          user.value = response.data
        } catch (error) {
          console.error('Error fetching user profile:', error)
        }
      }
    })

    function logout() {
      // Use the auth service to logout
      authService.logout()
      
      // Show notification
      $q.notify({
        color: 'positive',
        message: 'Successfully logged out',
        icon: 'logout'
      })
      
      // Redirect to login
      router.push('/auth/login')
    }
    
    return {
      user,
      leftDrawerOpen,
      toggleLeftDrawer () {
        leftDrawerOpen.value = !leftDrawerOpen.value
      },
      logout
    }
  }
}
</script>