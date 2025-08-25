<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <div class="row justify-center items-center" style="min-height: 100vh;">
        <div class="col-12 col-sm-8 col-md-6 col-lg-4">
          <q-card class="auth-card q-pa-lg">
            <q-card-section class="text-center">
              <div class="text-h5 q-mb-md">Nimo Platform</div>
              <div class="text-subtitle2 text-grey">Decentralized Youth Identity & Proof of Contribution Network</div>
            </q-card-section>

            <router-view />

            <q-card-section class="text-center q-pt-none">
              <div class="text-caption text-grey q-mt-sm">
                &copy; 2025 Nimo Platform
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </q-page-container>
  </q-layout>
</template>

<script>
export default {
  name: 'AuthLayout'
}
</script>

<style lang="scss" scoped>
.auth-card {
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}
</style>