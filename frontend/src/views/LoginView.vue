<script setup lang="ts">
import {ref} from 'vue';
import {useRouter} from 'vue-router';
import apiClient from '@/services/api';

const username = ref('');
const password = ref('');
const errorMessage = ref('');
const router = useRouter();

const handleLogin = async () => {
  errorMessage.value = '';

  try {
    await apiClient.get('/csrf/');

    const loginData = new URLSearchParams();
    loginData.append('username', username.value);
    loginData.append('password', password.value);

    await apiClient.post('/accounts/login/', loginData);

    // Langkah C: Jika berhasil (tidak ada error), redirect ke halaman utama
    alert('Login Berhasil!');
    router.push('/');

  } catch (error) {
    console.error('Proses login gagal:', error);
    errorMessage.value = 'Login gagal. Periksa kembali username dan password Anda.';
  }
};
</script>

<template>
  <div class="login-container">
    <h2>Login</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="username">Username</label>
        <input type="text" id="username" v-model="username" required/>
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" v-model="password" required/>
      </div>
      <button type="submit">Login</button>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    </form>
  </div>
</template>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 5rem auto;
  padding: 2rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

button {
  width: 100%;
  padding: 0.75rem;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
}

button:hover {
  background-color: #36a46f;
}

.error-message {
  color: #d9534f;
  margin-top: 1rem;
  text-align: center;
}
</style>
