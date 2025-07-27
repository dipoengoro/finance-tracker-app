<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';

const wallets = ref([]);

onMounted(async () => {
  try {
    const response = await apiClient.get('/api/wallets/');

    wallets.value = response.data;

    console.log('Data dompet berhasil diambil:', response.data);
  } catch (error) {
    console.error('Gagal mengambil data dompet:', error);
  }
});
</script>

<template>
  <div class="about">
    <h1>Daftar Dompet Saya</h1>

    <p v-if="wallets.length === 0">Memuat data dompet...</p>

    <ul v-else>
      <li v-for="wallet in wallets" :key="wallet.id">
        {{ wallet.name }} - ({{ wallet.wallet_type }}): Rp {{ wallet.balance }}
      </li>
    </ul>
  </div>
</template>

<style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    padding-top: 2rem;
  }
}
</style>
