import axios from 'axios';

// Membuat instance axios dengan konfigurasi default
const apiClient = axios.create({
  baseURL: 'http://localhost:8000', // URL dasar dari API Django kita
  withCredentials: true, // INI YANG PALING PENTING!
});

export default apiClient;
