<template>
  <q-page class="page-container">
    <div class="row q-col-gutter-md">
      <div class="col-12">
        <q-card>
          <q-card-section class="bg-primary text-white">
            <div class="text-h5">My Profile</div>
          </q-card-section>
          
          <q-card-section>
            <div class="row items-center q-mb-lg">
              <div class="col-auto">
                <q-avatar size="100px" color="grey-3" text-color="primary">
                  {{ userInitials }}
                </q-avatar>
              </div>
              <div class="col q-ml-md">
                <div class="text-h5">{{ user.name }}</div>
                <div class="text-subtitle2">{{ user.location }}</div>
                <q-badge color="primary" class="q-mr-xs" v-for="skill in user.skills" :key="skill">
                  {{ skill }}
                </q-badge>
              </div>
              <div class="col-auto">
                <q-btn color="primary" icon="edit" label="Edit Profile" />
              </div>
            </div>
            
            <q-separator class="q-my-md" />
            
            <div class="row q-col-gutter-md">
              <div class="col-12 col-md-6">
                <div class="text-h6">Personal Information</div>
                <q-list>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Email</q-item-label>
                      <q-item-label>{{ user.email }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Location</q-item-label>
                      <q-item-label>{{ user.location }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Member Since</q-item-label>
                      <q-item-label>{{ user.memberSince }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>
              
              <div class="col-12 col-md-6">
                <div class="text-h6">Skills</div>
                <q-list>
                  <q-item v-for="(skill, index) in user.skills" :key="index">
                    <q-item-section>
                      <q-item-label>{{ skill }}</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-btn flat round dense icon="close" color="negative" />
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-input filled dense v-model="newSkill" placeholder="Add a new skill" @keyup.enter="addSkill">
                        <template v-slot:append>
                          <q-btn round dense flat icon="add" @click="addSkill" />
                        </template>
                      </q-input>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>
            </div>
            
            <q-separator class="q-my-md" />
            
            <div class="row q-col-gutter-md">
              <div class="col-12">
                <div class="text-h6">Bio</div>
                <q-input
                  v-model="user.bio"
                  type="textarea"
                  filled
                  autogrow
                />
                <div class="row justify-end q-mt-sm">
                  <q-btn color="primary" label="Save Changes" />
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'ProfilePage',

  setup () {
    // Mock user data
    const user = ref({
      name: 'Kwame Johnson',
      email: 'kwame@example.com',
      location: 'Nairobi, Kenya',
      memberSince: 'January 15, 2025',
      skills: ['Python', 'JavaScript', 'Community Organizing'],
      bio: 'Software developer and community organizer passionate about youth empowerment and technology education.'
    })
    
    const newSkill = ref('')
    
    const userInitials = computed(() => {
      const nameParts = user.value.name.split(' ')
      return nameParts.map(part => part[0]).join('')
    })
    
    function addSkill() {
      if (newSkill.value.trim() !== '') {
        user.value.skills.push(newSkill.value.trim())
        newSkill.value = ''
      }
    }
    
    return {
      user,
      newSkill,
      userInitials,
      addSkill
    }
  }
}
</script>