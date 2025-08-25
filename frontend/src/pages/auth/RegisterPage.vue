<template>
  <q-page-container>
    <div class="row justify-center items-center" style="min-height: 100vh;">
      <div class="col-12 col-sm-8 col-md-6 col-lg-4">
        <q-card class="auth-card q-pa-lg">
          <q-card-section class="text-center">
            <div class="text-h5">Create an Account</div>
            <div class="text-subtitle2 text-grey">Register to start building your digital identity</div>
          </q-card-section>

          <q-card-section>
            <q-form @submit="onSubmit" class="q-gutter-md">
              <q-input
                filled
                v-model="name"
                label="Full Name"
                lazy-rules
                :rules="[ val => val && val.length > 0 || 'Please enter your name']"
              />

              <q-input
                filled
                v-model="email"
                label="Email"
                type="email"
                lazy-rules
                :rules="[
                  val => val && val.length > 0 || 'Please enter your email',
                  val => val.includes('@') || 'Please enter a valid email'
                ]"
              />

              <q-input
                filled
                v-model="location"
                label="Location"
                lazy-rules
                :rules="[ val => val && val.length > 0 || 'Please enter your location']"
              />

              <q-select
                filled
                v-model="skills"
                multiple
                use-chips
                use-input
                input-debounce="0"
                label="Skills"
                :options="skillOptions"
                @filter="filterSkills"
                new-value-mode="add-unique"
              />

              <q-input
                filled
                v-model="password"
                label="Password"
                :type="isPwd ? 'password' : 'text'"
                lazy-rules
                :rules="[ 
                  val => val && val.length > 0 || 'Please enter a password',
                  val => val.length >= 8 || 'Password must be at least 8 characters'
                ]"
              >
                <template v-slot:append>
                  <q-icon
                    :name="isPwd ? 'visibility_off' : 'visibility'"
                    class="cursor-pointer"
                    @click="isPwd = !isPwd"
                  />
                </template>
              </q-input>

              <q-input
                filled
                v-model="confirmPassword"
                label="Confirm Password"
                :type="isPwdConfirm ? 'password' : 'text'"
                lazy-rules
                :rules="[
                  val => val && val.length > 0 || 'Please confirm your password',
                  val => val === password || 'Passwords do not match'
                ]"
              >
                <template v-slot:append>
                  <q-icon
                    :name="isPwdConfirm ? 'visibility_off' : 'visibility'"
                    class="cursor-pointer"
                    @click="isPwdConfirm = !isPwdConfirm"
                  />
                </template>
              </q-input>

              <div>
                <q-checkbox v-model="agree" label="I agree to the Terms and Conditions" />
              </div>

              <div>
                <q-btn 
                  label="Register" 
                  type="submit" 
                  color="primary" 
                  class="full-width"
                  :disable="!agree"
                />
              </div>
            </q-form>
          </q-card-section>

          <q-card-section class="text-center">
            <p class="text-grey q-ma-none">Already have an account? 
              <router-link to="/auth/login" class="text-primary">Login</router-link>
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
  name: 'RegisterPage',

  setup() {
    const router = useRouter()
    const $q = useQuasar()
    
    const name = ref('')
    const email = ref('')
    const location = ref('')
    const skills = ref([])
    const password = ref('')
    const confirmPassword = ref('')
    const isPwd = ref(true)
    const isPwdConfirm = ref(true)
    const agree = ref(false)
    
    // Sample skills options
    const skillsList = [
      'Python', 'JavaScript', 'Community Organizing', 'Leadership',
      'Public Speaking', 'Project Management', 'Design', 'Education',
      'Web Development', 'Mobile Development', 'Data Analysis',
      'Digital Marketing', 'Content Creation', 'Environmental Science'
    ]
    const skillOptions = ref(skillsList)
    
    function filterSkills(val, update) {
      if (val === '') {
        update(() => {
          skillOptions.value = skillsList
        })
        return
      }

      update(() => {
        const needle = val.toLowerCase()
        skillOptions.value = skillsList.filter(
          v => v.toLowerCase().indexOf(needle) > -1
        )
      })
    }

    const onSubmit = () => {
      // In a real application, you would register with your backend
      // Here we're just simulating a successful registration
      
      // Show success notification
      $q.notify({
        color: 'positive',
        message: 'Successfully registered! Please log in.',
        icon: 'check'
      })
      
      // Redirect to login page
      router.push('/auth/login')
    }

    return {
      name,
      email,
      location,
      skills,
      skillOptions,
      password,
      confirmPassword,
      isPwd,
      isPwdConfirm,
      agree,
      filterSkills,
      onSubmit
    }
  }
}
</script>