import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: BASE_URL,
    timeout: 30000,
    headers: { 'Content-Type': 'application/json' },
  });

  // Request interceptor: inject JWT
  client.interceptors.request.use((config) => {
    const token = localStorage.getItem('planwise_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  // Response interceptor: handle 401
  client.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        localStorage.removeItem('planwise_token');
        localStorage.removeItem('planwise_user');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  return client;
};

export const api = createApiClient();

// ── Generic helpers ──────────────────────────────────────────────────────────

export const apiGet = async <T>(url: string, params?: Record<string, unknown>): Promise<T> => {
  const { data } = await api.get<T>(url, { params });
  return data;
};

export const apiPost = async <T>(url: string, body?: unknown): Promise<T> => {
  const { data } = await api.post<T>(url, body);
  return data;
};

export const apiPut = async <T>(url: string, body?: unknown): Promise<T> => {
  const { data } = await api.put<T>(url, body);
  return data;
};

export const apiDelete = async (url: string): Promise<void> => {
  await api.delete(url);
};
