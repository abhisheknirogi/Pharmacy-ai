import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '@/types';
import { apiClient } from '@/lib/api';

interface AuthStore {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;

  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  setToken: (token: string) => void;
  fetchUser: () => Promise<void>;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: false,
      isAuthenticated: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true });
        try {
          const data = await apiClient.login(email, password);
          const user = await apiClient.getMe();
          set({
            user,
            token: data.access_token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      register: async (email: string, password: string, fullName?: string) => {
        set({ isLoading: true });
        try {
          const user = await apiClient.register(email, password, fullName);
          set({ user, isLoading: false });
          // After registration, auto-login
          await get().login(email, password);
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: () => {
        apiClient.setToken(null);
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
      },

      setToken: (token: string) => {
        apiClient.setToken(token);
        set({ token });
      },

      fetchUser: async () => {
        try {
          const user = await apiClient.getMe();
          set({ user, isAuthenticated: true });
        } catch (error) {
          set({ isAuthenticated: false });
          throw error;
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token, user: state.user }),
    }
  )
);
