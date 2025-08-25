<template>
  <q-page-container>
    <div class="row justify-center items-center" style="min-height: 100vh;">
      <div class="col-12 col-sm-8 col-md-6 col-lg-4">
        <q-card class="auth-card q-pa-lg">
          <q-card-section class="text-center">
            <div class="text-h5">Welcome Back</div>
            <div class="text-subtitle2 text-grey">Login to your account</div>
          </q-card-section>

          <q-card-section>
            <q-form @submit="onSubmit" class="q-gutter-md">
              <q-input
                filled
                v-model="email"
                label="Email"
                type="email"
                lazy-rules
                :rules="[ val => val && val.length > 0 || 'Please enter your email']"
              />

              <q-input
                filled
                v-model="password"
                label="Password"
                :type="isPwd ? 'password' : 'text'"
                lazy-rules
                :rules="[ val => val && val.length > 0 || 'Please enter your password']"
              >
                <template v-slot:append>
                  <q-icon
                    :name="isPwd ? 'visibility_off' : 'visibility'"
                    class="cursor-pointer"
                    @click="isPwd = !isPwd"
                  />
                </template>
              </q-input>

              <div>
                <q-checkbox v-model="remember" label="Remember me" />
              </div>

              <div>
                <q-btn 
                  label="Login" 
                  type="submit" 
                  color="primary" 
                  class="full-width"
                />
              </div>
            </q-form>
          </q-card-section>

          <q-card-section class="text-center">
            <p class="text-grey q-ma-none">Don't have an account? 
              <router-link to="/auth/register" class="text-primary">Register</router-link>
            </p>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page-container>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'

export default {
  name: 'LoginPage',

  setup() {
    const router = useRouter()
    const $q = useQuasar()
    
    const email = ref('')
    const password = ref('')
    const isPwd = ref(true)
    const remember = ref(false)

    const onSubmit = () => {
      // In a real application, you would authenticate with your backend
      // Here we're just simulating a successful login
      
      // Store the token in local storage
      localStorage.setItem('token', 'mock-jwt-token')
      
      // Show success notification
      $q.notify({
        color: 'positive',
        message: 'Successfully logged in',
        icon: 'check'
      })
      
      // Redirect to home page
      router.push('/')
    }

    return {
      email,
      password,
      isPwd,
      remember,
      onSubmit
    }
  }
}
</script>