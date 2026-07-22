import axios from 'axios';
import { getFirebaseAuth } from './firebase';

const backendUrl = import.meta.env.VITE_BACKEND_URL || '';

export const apiClient = axios.create({
  baseURL: backendUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(async (config) => {
  try {
    const auth = getFirebaseAuth();
    const currentUser = auth.currentUser;
    if (currentUser) {
      const token = await currentUser.getIdToken();
      config.headers.Authorization = `Bearer ${token}`;
    }
  } catch (err) {
    console.error("Failed to attach auth token", err);
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

