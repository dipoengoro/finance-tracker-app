import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'https://www.amalindipo.id',
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
});

export default apiClient;
