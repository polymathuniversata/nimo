<template>
  <q-page class="page-container">
    <div class="row q-col-gutter-md">
      <div class="col-12">
        <q-card>
          <q-card-section class="bg-primary text-white">
            <div class="text-h5">Impact Bonds</div>
            <div class="text-subtitle2">NFT-backed diaspora bonds for funding local initiatives</div>
          </q-card-section>
          
          <q-card-actions>
            <q-btn color="primary" icon="add" label="Create New Impact Bond" @click="showCreateDialog = true" />
            <q-space />
            <q-select
              v-model="causeFilter"
              :options="causeOptions"
              label="Filter by cause"
              dense
              outlined
              style="width: 200px"
              emit-value
              map-options
              clearable
            />
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
            <q-tab name="active" label="Active Bonds" />
            <q-tab name="my" label="My Bonds" />
            <q-tab name="investments" label="My Investments" />
          </q-tabs>

          <q-separator />

          <q-tab-panels v-model="tab" animated>
            <q-tab-panel name="active">
              <div class="row q-col-gutter-md">
                <div v-for="bond in filteredBonds" :key="bond.id" class="col-12 col-md-6 col-lg-4">
                  <bond-card :bond="bond" @invest="openInvestDialog" />
                </div>
                <div v-if="filteredBonds.length === 0" class="col-12 text-center q-pa-md">
                  <q-icon name="search_off" size="48px" color="grey" />
                  <div class="text-h6 text-grey">No active bonds found</div>
                </div>
              </div>
            </q-tab-panel>

            <q-tab-panel name="my">
              <div class="row q-col-gutter-md">
                <div v-for="bond in myBonds" :key="bond.id" class="col-12 col-md-6 col-lg-4">
                  <bond-card :bond="bond" :is-owner="true" @add-milestone="openAddMilestoneDialog" />
                </div>
                <div v-if="myBonds.length === 0" class="col-12 text-center q-pa-md">
                  <q-icon name="info" size="48px" color="grey" />
                  <div class="text-h6 text-grey">You haven't created any bonds yet</div>
                  <q-btn color="primary" label="Create your first impact bond" class="q-mt-md" @click="showCreateDialog = true" />
                </div>
              </div>
            </q-tab-panel>

            <q-tab-panel name="investments">
              <div class="row q-col-gutter-md">
                <div v-for="investment in myInvestments" :key="investment.id" class="col-12 col-md-6 col-lg-4">
                  <investment-card :investment="investment" />
                </div>
                <div v-if="myInvestments.length === 0" class="col-12 text-center q-pa-md">
                  <q-icon name="account_balance" size="48px" color="grey" />
                  <div class="text-h6 text-grey">You haven't invested in any bonds yet</div>
                  <q-btn color="primary" label="Browse available bonds" class="q-mt-md" @click="tab = 'active'" />
                </div>
              </div>
            </q-tab-panel>
          </q-tab-panels>
        </q-card>
      </div>
    </div>
    
    <!-- Create Impact Bond Dialog -->
    <q-dialog v-model="showCreateDialog">
      <q-card style="width: 700px; max-width: 90vw;">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6">Create New Impact Bond</div>
        </q-card-section>
        
        <q-card-section>
          <q-form @submit="createBond" class="q-gutter-md">
            <q-input 
              v-model="newBond.title" 
              label="Title" 
              filled 
              :rules="[val => !!val || 'Title is required']"
            />
            
            <q-input 
              v-model="newBond.description" 
              label="Description" 
              type="textarea"
              filled 
              autogrow 
            />
            
            <q-select
              v-model="newBond.cause"
              :options="causeOptions"
              label="Cause"
              filled
              emit-value
              map-options
            />
            
            <q-input 
              v-model="newBond.value" 
              label="Value (tokens)" 
              filled 
              type="number"
              :rules="[
                val => !!val || 'Value is required',
                val => val > 0 || 'Value must be greater than 0'
              ]"
            />
            
            <q-input 
              v-model="newBond.image_url" 
              label="Image URL (optional)" 
              filled 
            />
            
            <div class="text-h6 q-mt-md">Milestones</div>
            <div v-for="(milestone, index) in newBond.milestones" :key="index" class="row q-col-gutter-sm q-mb-sm">
              <div class="col">
                <q-input 
                  v-model="milestone.milestone" 
                  label="Milestone" 
                  filled 
                  dense
                />
              </div>
              <div class="col-auto">
                <q-btn round flat color="negative" icon="delete" @click="removeMilestone(index)" />
              </div>
            </div>
            
            <div class="row justify-center q-mt-sm">
              <q-btn color="grey" icon="add" label="Add Milestone" @click="addMilestone" />
            </div>
          </q-form>
        </q-card-section>
        
        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="negative" v-close-popup />
          <q-btn label="Create" color="primary" @click="createBond" />
        </q-card-actions>
      </q-card>
    </q-dialog>
    
    <!-- Invest Dialog -->
    <q-dialog v-model="showInvestDialog">
      <q-card style="width: 500px; max-width: 80vw;">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6">Invest in {{ selectedBond?.title }}</div>
        </q-card-section>
        
        <q-card-section>
          <div class="text-subtitle2 q-mb-md">
            Your current token balance: <strong>{{ tokenBalance }}</strong>
          </div>
          
          <q-input 
            v-model="investAmount" 
            label="Amount to invest (tokens)" 
            type="number"
            filled 
            :rules="[
              val => !!val || 'Amount is required',
              val => val > 0 || 'Amount must be greater than 0',
              val => val <= tokenBalance || 'Insufficient token balance'
            ]"
          />
        </q-card-section>
        
        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="negative" v-close-popup />
          <q-btn label="Invest" color="primary" @click="investInBond" :disable="!investAmount || investAmount <= 0 || investAmount > tokenBalance" />
        </q-card-actions>
      </q-card>
    </q-dialog>
    
    <!-- Add Milestone Dialog -->
    <q-dialog v-model="showAddMilestoneDialog">
      <q-card style="width: 500px; max-width: 80vw;">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6">Add Milestone to {{ selectedBond?.title }}</div>
        </q-card-section>
        
        <q-card-section>
          <q-input 
            v-model="newMilestone.milestone" 
            label="Milestone" 
            filled 
            :rules="[val => !!val || 'Milestone description is required']"
          />
          
          <q-input 
            v-model="newMilestone.evidence" 
            label="Evidence URL (optional)" 
            filled 
            class="q-mt-md"
          />
        </q-card-section>
        
        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="negative" v-close-popup />
          <q-btn label="Add" color="primary" @click="addMilestoneToBond" :disable="!newMilestone.milestone" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import BondCard from 'components/bonds/BondCard.vue'
import InvestmentCard from 'components/bonds/InvestmentCard.vue'
import { bondService, tokenService } from 'src/services'

export default {
  name: 'BondsPage',
  
  components: {
    BondCard,
    InvestmentCard
  },

  setup() {
    const $q = useQuasar()
    const tab = ref('active')
    const causeFilter = ref(null)
    const showCreateDialog = ref(false)
    const showInvestDialog = ref(false)
    const showAddMilestoneDialog = ref(false)
    const loading = ref(false)
    
    // Data refs
    const tokenBalance = ref(0)
    const bonds = ref([])
    const myBonds = ref([])
    const myInvestments = ref([])

    // Load data on component mount
    onMounted(() => {
      loadTokenBalance()
      loadBonds()
      loadMyBonds()
      loadMyInvestments()
    })
    
    // Load user's token balance
    async function loadTokenBalance() {
      try {
        const response = await tokenService.getTokenBalance()
        tokenBalance.value = response.data.balance
      } catch (error) {
        console.error('Error fetching token balance:', error)
        $q.notify({
          type: 'negative',
          message: 'Failed to load token balance',
          icon: 'error'
        })
      }
    }
    
    // Load active bonds
    async function loadBonds() {
      loading.value = true
      try {
        const response = await bondService.getActiveBonds()
        bonds.value = response.data.bonds
      } catch (error) {
        console.error('Error fetching bonds:', error)
        $q.notify({
          type: 'negative',
          message: 'Failed to load active bonds',
          icon: 'error'
        })
        // Fallback to mock data if API fails
        bonds.value = [
          {
            id: 1,
            bond_id: 'climate-001',
            creator_id: 3,
            creator_name: 'Chidi',
            title: 'Reforestation Project in Mau Forest',
            description: 'Planting trees to restore the Mau Forest ecosystem and fight climate change',
            cause: 'climate',
            value: 10000,
            image_url: 'https://example.com/forest.jpg',
            created_at: '2025-08-15T10:30:00',
            status: 'active',
            total_investment: 3500,
            funding_percentage: 35,
            milestone_count: 3,
            verified_milestones: 1,
            progress_percentage: 33
          },
          {
            id: 2,
            bond_id: 'edu-001',
            creator_id: 1,
            creator_name: 'Kwame',
            title: 'Coding Bootcamp for Underprivileged Youth',
            description: 'Providing programming education to youth from disadvantaged backgrounds',
            cause: 'education',
            value: 8000,
            image_url: 'https://example.com/coding.jpg',
            created_at: '2025-08-10T14:20:00',
            status: 'active',
            total_investment: 6000,
            funding_percentage: 75,
            milestone_count: 4,
            verified_milestones: 2,
            progress_percentage: 50
          },
          {
            id: 3,
            bond_id: 'community-001',
            creator_id: 2,
            creator_name: 'Ada',
            title: "Women's Entrepreneurship Network",
            description: 'Supporting women entrepreneurs in starting and growing their businesses',
            cause: 'economic-empowerment',
            value: 5000,
            image_url: 'https://example.com/women-entrepreneurs.jpg',
            created_at: '2025-08-05T09:15:00',
            status: 'active',
            total_investment: 4500,
            funding_percentage: 90,
            milestone_count: 3,
            verified_milestones: 2,
            progress_percentage: 66
          }
        ]
      } finally {
        loading.value = false
      }
    }
    
    // Load user's bonds
    async function loadMyBonds() {
      try {
        const response = await bondService.getUserBonds()
        myBonds.value = response.data.bonds
      } catch (error) {
        console.error('Error fetching user bonds:', error)
        $q.notify({
          type: 'negative',
          message: 'Failed to load your bonds',
          icon: 'error'
        })
        // Fallback to mock data if API fails
        myBonds.value = [
          {
            id: 4,
            bond_id: 'tech-001',
            creator_id: 1,
            creator_name: 'Current User',
            title: 'Mobile App for Community Health',
            description: 'Developing a mobile application to connect rural communities with health resources',
            cause: 'health',
            value: 7000,
            image_url: 'https://example.com/health-app.jpg',
            created_at: '2025-08-01T11:45:00',
            status: 'active',
            total_investment: 2100,
            funding_percentage: 30,
            milestone_count: 5,
            verified_milestones: 1,
            progress_percentage: 20
          }
        ]
      }
    }
    
    // Load user's investments
    async function loadMyInvestments() {
      try {
        const response = await bondService.getUserInvestments()
        myInvestments.value = response.data.investments
      } catch (error) {
        console.error('Error fetching user investments:', error)
        $q.notify({
          type: 'negative',
          message: 'Failed to load your investments',
          icon: 'error'
        })
        // Fallback to mock data if API fails
        myInvestments.value = [
          {
            id: 1,
            bond_id: 2,
            bond_title: 'Coding Bootcamp for Underprivileged Youth',
            investor_id: 1,
            investor_name: 'Current User',
            amount: 1000,
            created_at: '2025-08-12T16:30:00'
          },
          {
            id: 2,
            bond_id: 3,
            bond_title: "Women's Entrepreneurship Network",
            investor_id: 1,
            investor_name: 'Current User',
            amount: 500,
            created_at: '2025-08-08T14:15:00'
          }
        ]
      }
    }
    
    const causeOptions = [
      { label: 'Climate Action', value: 'climate' },
      { label: 'Education', value: 'education' },
      { label: 'Economic Empowerment', value: 'economic-empowerment' },
      { label: 'Health', value: 'health' },
      { label: 'Technology', value: 'technology' },
      { label: 'Agriculture', value: 'agriculture' },
      { label: 'Arts & Culture', value: 'arts' }
    ]
    
    // Form models
    const newBond = ref({
      title: '',
      description: '',
      cause: '',
      value: null,
      image_url: '',
      milestones: [{ milestone: '', evidence: '' }]
    })
    
    const selectedBond = ref(null)
    const investAmount = ref(null)
    const newMilestone = ref({ milestone: '', evidence: '' })
    
    // Computed properties
    const filteredBonds = computed(() => {
      if (!causeFilter.value) return bonds.value
      return bonds.value.filter(bond => bond.cause === causeFilter.value)
    })
    
    // Form models
    const newBond = ref({
      title: '',
      description: '',
      cause: '',
      value: null,
      image_url: '',
      milestones: [{ milestone: '', evidence: '' }]
    })
    
    const selectedBond = ref(null)
    const investAmount = ref(null)
    const newMilestone = ref({ milestone: '', evidence: '' })
    
    // Methods
    function addMilestone() {
      newBond.value.milestones.push({ milestone: '', evidence: '' })
    }
    
    function removeMilestone(index) {
      newBond.value.milestones.splice(index, 1)
      if (newBond.value.milestones.length === 0) {
        addMilestone()
      }
    }
    
    async function createBond() {
      if (!newBond.value.title || !newBond.value.value) {
        $q.notify({
          type: 'warning',
          message: 'Please fill all required fields',
          icon: 'warning'
        })
        return
      }
      
      // Show loading indicator
      $q.loading.show({
        message: 'Creating impact bond...'
      })
      
      try {
        // Send to API
        const response = await bondService.createBond({
          title: newBond.value.title,
          description: newBond.value.description,
          cause: newBond.value.cause,
          value: parseInt(newBond.value.value),
          image_url: newBond.value.image_url,
          milestones: newBond.value.milestones
        })
        
        // Add to myBonds
        myBonds.value.unshift(response.data)
        
        // Show success notification
        $q.notify({
          type: 'positive',
          message: 'Impact bond created successfully',
          icon: 'check_circle'
        })
        
        // Reset form
        newBond.value = {
          title: '',
          description: '',
          cause: '',
          value: null,
          image_url: '',
          milestones: [{ milestone: '', evidence: '' }]
        }
        
        // Close dialog
        showCreateDialog.value = false
      } catch (error) {
        console.error('Error creating bond:', error)
        $q.notify({
          type: 'negative',
          message: 'Failed to create impact bond',
          icon: 'error'
        })
        
        // Fallback: create bond with mock data if API fails
        const newId = Math.max(...[...bonds.value, ...myBonds.value].map(b => b.id)) + 1
        
        const createdBond = {
          id: newId,
          bond_id: `${newBond.value.cause || 'bond'}-${newId.toString().padStart(3, '0')}`,
          creator_id: 1,
          creator_name: 'Current User',
          title: newBond.value.title,
          description: newBond.value.description,
          cause: newBond.value.cause,
          value: parseInt(newBond.value.value),
          image_url: newBond.value.image_url,
          created_at: new Date().toISOString(),
          status: 'active',
          total_investment: 0,
          funding_percentage: 0,
          milestone_count: newBond.value.milestones.length,
          verified_milestones: 0,
          progress_percentage: 0
        }
        
        // Add to myBonds
        myBonds.value.unshift(createdBond)
        
        // Reset form and close dialog
        newBond.value = {
          title: '',
          description: '',
          cause: '',
          value: null,
          image_url: '',
          milestones: [{ milestone: '', evidence: '' }]
        }
        showCreateDialog.value = false
      } finally {
        $q.loading.hide()
      }
    }
    
    function openInvestDialog(bond) {
      selectedBond.value = bond
      investAmount.value = null
      showInvestDialog.value = true
    }
    
    function openAddMilestoneDialog(bond) {
      selectedBond.value = bond
      newMilestone.value = { milestone: '', evidence: '' }
      showAddMilestoneDialog.value = true
    }
    
    async function investInBond() {
      if (!selectedBond.value || !investAmount.value || investAmount.value <= 0 || investAmount.value > tokenBalance.value) {
        return
      }
      
      // Show loading indicator
      $q.loading.show({
        message: 'Processing investment...'
      })
      
      try {
        // Send to API
        const response = await bondService.investInBond(
          selectedBond.value.id, 
          parseInt(investAmount.value)
        )
        
        // Update token balance
        tokenBalance.value -= parseInt(investAmount.value)
        
        // Refresh investments list
        await loadMyInvestments()
        
        // Update bond funding in the active bonds list
        await loadBonds()
        
        // Show success notification
        $q.notify({
          type: 'positive',
          message: 'Investment successful!',
          icon: 'check_circle'
        })
        
        // Close dialog
        showInvestDialog.value = false
      } catch (error) {
        console.error('Error investing in bond:', error)
        $q.notify({
          type: 'negative',
          message: 'Failed to process investment',
          icon: 'error'
        })
        
        // Fallback: update local data if API fails
        // Create new investment record
        const newInvestment = {
          id: myInvestments.value.length + 1,
          bond_id: selectedBond.value.id,
          bond_title: selectedBond.value.title,
          investor_id: 1,
          investor_name: 'Current User',
          amount: parseInt(investAmount.value),
          created_at: new Date().toISOString()
        }
        
        // Add to myInvestments
        myInvestments.value.unshift(newInvestment)
        
        // Update bond funding
        const bondIndex = bonds.value.findIndex(b => b.id === selectedBond.value.id)
        if (bondIndex !== -1) {
          bonds.value[bondIndex].total_investment += parseInt(investAmount.value)
          bonds.value[bondIndex].funding_percentage = Math.floor(
            (bonds.value[bondIndex].total_investment / bonds.value[bondIndex].value) * 100
          )
        }
        
        // Deduct from token balance
        tokenBalance.value -= parseInt(investAmount.value)
        
        // Close dialog
        showInvestDialog.value = false
      } finally {
        $q.loading.hide()
      }
    }
    
    async function addMilestoneToBond() {
      if (!selectedBond.value || !newMilestone.value.milestone) {
        return
      }
      
      // Show loading indicator
      $q.loading.show({
        message: 'Adding milestone...'
      })
      
      try {
        // Send to API
        await bondService.addMilestone(
          selectedBond.value.id,
          newMilestone.value
        )
        
        // Refresh bonds list to get updated milestone data
        await loadMyBonds()
        
        // Show success notification
        $q.notify({
          type: 'positive',
          message: 'Milestone added successfully',
          icon: 'check_circle'
        })
        
        // Close dialog
        showAddMilestoneDialog.value = false
      } catch (error) {
        console.error('Error adding milestone:', error)
        $q.notify({
          type: 'negative',
          message: 'Failed to add milestone',
          icon: 'error'
        })
        
        // Fallback: update local data if API fails
        const bondIndex = myBonds.value.findIndex(b => b.id === selectedBond.value.id)
        if (bondIndex !== -1) {
          myBonds.value[bondIndex].milestone_count += 1
          myBonds.value[bondIndex].progress_percentage = Math.floor(
            (myBonds.value[bondIndex].verified_milestones / myBonds.value[bondIndex].milestone_count) * 100
          )
        }
        
        // Close dialog
        showAddMilestoneDialog.value = false
      } finally {
        $q.loading.hide()
      }
    }
    
    const causeOptions = [
      { label: 'Climate Action', value: 'climate' },
      { label: 'Education', value: 'education' },
      { label: 'Economic Empowerment', value: 'economic-empowerment' },
      { label: 'Health', value: 'health' },
      { label: 'Technology', value: 'technology' },
      { label: 'Agriculture', value: 'agriculture' },
      { label: 'Arts & Culture', value: 'arts' }
    ]
    
    // Computed properties
    const filteredBonds = computed(() => {
      if (!causeFilter.value) return bonds.value
      return bonds.value.filter(bond => bond.cause === causeFilter.value)
    })
    
    return {
      tab,
      causeFilter,
      causeOptions,
      bonds,
      myBonds,
      myInvestments,
      filteredBonds,
      tokenBalance,
      showCreateDialog,
      newBond,
      addMilestone,
      removeMilestone,
      createBond,
      showInvestDialog,
      selectedBond,
      investAmount,
      openInvestDialog,
      investInBond,
      showAddMilestoneDialog,
      newMilestone,
      openAddMilestoneDialog,
      addMilestoneToBond
    }
  }
}
</script>

<style lang="scss" scoped>
.bond-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}
</style>