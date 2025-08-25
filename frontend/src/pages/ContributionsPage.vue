<template>
  <q-page class="page-container">
    <div class="row q-col-gutter-md">
      <div class="col-12">
        <q-card>
          <q-card-section class="bg-primary text-white">
            <div class="text-h5">Contributions</div>
            <div class="text-subtitle2">Record and track your contributions</div>
          </q-card-section>
          
          <q-card-actions>
            <q-btn color="primary" icon="add" label="Add New Contribution" @click="showAddDialog = true" />
          </q-card-actions>
          
          <q-tabs
            v-model="tab"
            dense
            class="text-grey"
            active-color="primary"
            indicator-color="primary"
            align="justify"
            narrow-indicator
          >
            <q-tab name="all" label="All" />
            <q-tab name="verified" label="Verified" />
            <q-tab name="pending" label="Pending Verification" />
          </q-tabs>

          <q-separator />

          <q-tab-panels v-model="tab" animated>
            <q-tab-panel name="all">
              <div class="q-mb-md">
                <q-input filled v-model="search" label="Search contributions" dense>
                  <template v-slot:append>
                    <q-icon name="search" />
                  </template>
                </q-input>
              </div>
              
              <q-list separator>
                <q-item v-for="contribution in filteredContributions" :key="contribution.id">
                  <q-item-section avatar>
                    <q-avatar :color="contribution.verified ? 'positive' : 'grey'" text-color="white">
                      <q-icon :name="contribution.verified ? 'check' : 'pending'" />
                    </q-avatar>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ contribution.title }}</q-item-label>
                    <q-item-label caption>{{ contribution.description }}</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <div class="text-caption text-grey">{{ contribution.date }}</div>
                    <q-badge :color="contribution.verified ? 'positive' : 'grey'">
                      {{ contribution.verified ? 'Verified' : 'Pending' }}
                    </q-badge>
                    <div v-if="contribution.verified" class="text-caption">
                      by {{ contribution.verifier }}
                    </div>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-tab-panel>

            <q-tab-panel name="verified">
              <q-list separator>
                <q-item v-for="contribution in verifiedContributions" :key="contribution.id">
                  <q-item-section avatar>
                    <q-avatar color="positive" text-color="white">
                      <q-icon name="check" />
                    </q-avatar>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ contribution.title }}</q-item-label>
                    <q-item-label caption>{{ contribution.description }}</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <div class="text-caption text-grey">{{ contribution.date }}</div>
                    <q-badge color="positive">Verified</q-badge>
                    <div class="text-caption">by {{ contribution.verifier }}</div>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-tab-panel>

            <q-tab-panel name="pending">
              <q-list separator>
                <q-item v-for="contribution in pendingContributions" :key="contribution.id">
                  <q-item-section avatar>
                    <q-avatar color="grey" text-color="white">
                      <q-icon name="pending" />
                    </q-avatar>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ contribution.title }}</q-item-label>
                    <q-item-label caption>{{ contribution.description }}</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <div class="text-caption text-grey">{{ contribution.date }}</div>
                    <q-badge color="grey">Pending</q-badge>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-tab-panel>
          </q-tab-panels>
        </q-card>
      </div>
    </div>
    
    <!-- Add Contribution Dialog -->
    <q-dialog v-model="showAddDialog">
      <q-card style="width: 500px; max-width: 80vw;">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6">Add New Contribution</div>
        </q-card-section>
        
        <q-card-section>
          <q-input 
            v-model="newContribution.title" 
            label="Contribution Title" 
            filled 
            :rules="[val => !!val || 'Title is required']"
            class="q-mb-md"
          />
          
          <q-input 
            v-model="newContribution.description" 
            label="Description" 
            type="textarea"
            filled 
            autogrow 
            class="q-mb-md"
          />
          
          <q-select
            v-model="newContribution.type"
            :options="contributionTypes"
            label="Contribution Type"
            filled
            class="q-mb-md"
          />
          
          <q-input 
            v-model="newContribution.evidence" 
            label="Evidence URL (optional)" 
            filled 
            class="q-mb-md"
          />
          
          <q-select
            v-model="newContribution.organization"
            :options="organizations"
            label="Verifying Organization"
            filled
            class="q-mb-md"
          />
        </q-card-section>
        
        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="negative" v-close-popup />
          <q-btn label="Submit" color="primary" @click="addContribution" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'ContributionsPage',

  setup () {
    const tab = ref('all')
    const search = ref('')
    const showAddDialog = ref(false)
    
    // Mock data
    const contributions = ref([
      {
        id: 1,
        title: 'KRNL Hackathon',
        description: 'Participated in the KRNL Hackathon and built a decentralized application',
        date: 'Aug 10, 2025',
        verified: true,
        verifier: 'KRNL_Org',
        type: 'coding'
      },
      {
        id: 2,
        title: 'Community Workshop',
        description: 'Hosted a workshop teaching basic programming to youth',
        date: 'Jul 15, 2025',
        verified: true,
        verifier: 'Tech Community',
        type: 'education'
      },
      {
        id: 3,
        title: 'Open Source Project',
        description: 'Contributed to an open-source library for educational games',
        date: 'Aug 20, 2025',
        verified: false,
        type: 'coding'
      }
    ])
    
    const newContribution = ref({
      title: '',
      description: '',
      type: '',
      evidence: '',
      organization: ''
    })
    
    const contributionTypes = [
      'coding',
      'education',
      'volunteer',
      'activism',
      'leadership',
      'entrepreneurship'
    ]
    
    const organizations = [
      'KRNL_Org',
      'Tech Community',
      'Youth NGO',
      'Environmental NGO',
      'Community Council'
    ]
    
    // Computed properties for filtered lists
    const filteredContributions = computed(() => {
      if (!search.value) return contributions.value
      const searchLower = search.value.toLowerCase()
      return contributions.value.filter(c => 
        c.title.toLowerCase().includes(searchLower) || 
        c.description.toLowerCase().includes(searchLower)
      )
    })
    
    const verifiedContributions = computed(() => 
      contributions.value.filter(c => c.verified)
    )
    
    const pendingContributions = computed(() => 
      contributions.value.filter(c => !c.verified)
    )
    
    function addContribution() {
      // Add the new contribution to the list
      contributions.value.push({
        id: contributions.value.length + 1,
        title: newContribution.value.title,
        description: newContribution.value.description,
        date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
        verified: false,
        type: newContribution.value.type
      })
      
      // Reset form and close dialog
      newContribution.value = {
        title: '',
        description: '',
        type: '',
        evidence: '',
        organization: ''
      }
      
      showAddDialog.value = false
    }
    
    return {
      tab,
      search,
      showAddDialog,
      contributions,
      filteredContributions,
      verifiedContributions,
      pendingContributions,
      newContribution,
      contributionTypes,
      organizations,
      addContribution
    }
  }
}
</script>