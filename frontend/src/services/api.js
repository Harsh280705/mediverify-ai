import axios from 'axios';

const backendUrl = import.meta.env.VITE_BACKEND_URL || '';

export const apiClient = axios.create({
  baseURL: backendUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});
