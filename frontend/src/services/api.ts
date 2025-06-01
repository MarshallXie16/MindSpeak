import axios from 'axios';

/**
 * API configuration for the MindSpeak backend
 * Handles authentication tokens and base URL setup
 */

// Base URL for API requests - defaults to localhost for development
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear auth and redirect to login
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API endpoints
export const authAPI = {
  register: (data: { email: string; password: string; username?: string }) =>
    api.post('/auth/register', data),
  
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  
  logout: () => api.post('/auth/logout'),
  
  getMe: () => api.get('/auth/me'),
};

// Journal entries API endpoints (TODO: implement when backend is ready)
export const entriesAPI = {
  // TODO: Add entry-related API calls
  uploadAudio: (formData: FormData) =>
    api.post('/entries/upload-audio', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  
  getEntries: (params?: { page?: number; limit?: number }) =>
    api.get('/entries', { params }),
  
  getEntry: (id: number) => api.get(`/entries/${id}`),
  
  updateEntry: (id: number, data: any) => api.put(`/entries/${id}`, data),
  
  deleteEntry: (id: number) => api.delete(`/entries/${id}`),
  
  processEntry: (id: number) => api.post(`/entries/${id}/process`),
  
  getStats: () => api.get('/entries/stats'),
  
  getTrash: () => api.get('/entries/trash'),
  
  hardDeleteAll: () => api.delete('/entries/hard-delete-all'),
  
  fixStreaks: () => api.post('/entries/fix-streaks'),
};

// User preferences API endpoints
export const userAPI = {
  getProfile: () => api.get('/user/profile'),
  
  updateProfile: (data: any) => api.put('/user/profile', data),
  
  getPreferences: () => api.get('/user/preferences'),
  
  updatePreferences: (data: any) => api.put('/user/preferences', data),
  
  addGoal: (goalText: string) => api.post('/user/preferences/goals', { text: goalText }),
  
  removeGoal: (goalId: number) => api.delete(`/user/preferences/goals/${goalId}`),
};

export default api;