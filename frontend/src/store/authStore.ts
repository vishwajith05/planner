import { create } from 'zustand';
import { User, AuthTokens } from '../types';
import { apiGet, apiPost } from '../services/api';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  initialize: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('planwise_token'),
  isAuthenticated: !!localStorage.getItem('planwise_token'),
  isLoading: true,
  error: null,

  initialize: async () => {
    const token = localStorage.getItem('planwise_token');
    if (!token) {
      set({ isLoading: false, isAuthenticated: false, user: null });
      return;
    }
    try {
      const user = await apiGet<User>('/auth/me');
      set({ user, isAuthenticated: true, isLoading: false, error: null });
    } catch {
      localStorage.removeItem('planwise_token');
      set({ user: null, token: null, isAuthenticated: false, isLoading: false });
    }
  },

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const res = await apiPost<AuthTokens>('/auth/login', { email, password });
      localStorage.setItem('planwise_token', res.access_token);
      set({
        token: res.access_token,
        user: res.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Login failed';
      set({ error: msg, isLoading: false });
      throw new Error(msg);
    }
  },

  register: async (email: string, password: string, fullName?: string) => {
    set({ isLoading: true, error: null });
    try {
      await apiPost('/auth/register', {
        email,
        password,
        full_name: fullName,
      });
      // Automatically login after successful registration
      const res = await apiPost<AuthTokens>('/auth/login', { email, password });
      localStorage.setItem('planwise_token', res.access_token);
      set({
        token: res.access_token,
        user: res.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Registration failed';
      set({ error: msg, isLoading: false });
      throw new Error(msg);
    }
  },

  logout: () => {
    localStorage.removeItem('planwise_token');
    set({ user: null, token: null, isAuthenticated: false, error: null });
  },
}));
