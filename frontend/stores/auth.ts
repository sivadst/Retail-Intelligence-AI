"""Zustand auth store."""
import { create } from "zustand";
import { User, TokenResponse } from "@/types";
import { api } from "@/lib/api";

interface AuthState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  setUser: (user: User | null) => void;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, full_name: string, organization_name?: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchCurrentUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: false,
  error: null,

  setUser: (user) => set({ user }),

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.post<TokenResponse>("/auth/login", { email, password });
      localStorage.setItem("access_token", response.data.access_token);
      localStorage.setItem("refresh_token", response.data.refresh_token);

      const userResponse = await api.get<User>("/auth/me");
      set({ user: userResponse.data, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || "Login failed",
        isLoading: false,
      });
      throw error;
    }
  },

  register: async (email: string, password: string, full_name: string, organization_name?: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.post<TokenResponse>("/auth/register", {
        email,
        password,
        full_name,
        organization_name,
      });
      localStorage.setItem("access_token", response.data.access_token);
      localStorage.setItem("refresh_token", response.data.refresh_token);

      const userResponse = await api.get<User>("/auth/me");
      set({ user: userResponse.data, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || "Registration failed",
        isLoading: false,
      });
      throw error;
    }
  },

  logout: async () => {
    try {
      await api.post("/auth/logout");
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      set({ user: null });
    }
  },

  fetchCurrentUser: async () => {
    set({ isLoading: true });
    try {
      const response = await api.get<User>("/auth/me");
      set({ user: response.data, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
    }
  },
}));
