import { create } from "zustand";
import { persist } from "zustand/middleware";
import { authAPI } from "../api/auth.api";
import { tokenUtils } from "../utils/token";

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      loading: false,
      error: null,

      setTokens: (accessToken, refreshToken) => {
        tokenUtils.setTokens(accessToken, refreshToken);
        set({ accessToken, refreshToken });
      },

      login: async (email, password) => {
        set({ loading: true, error: null });
        try {
          const data = await authAPI.login(email, password);
          const { access, refresh, user } = data;

          tokenUtils.setTokens(access, refresh);

          set({
            user: user || null,
            accessToken: access,
            refreshToken: refresh,
            isAuthenticated: true,
            loading: false,
            error: null,
          });

          if (!user) {
            await get().fetchMe();
          }

          return { success: true };
        } catch (error) {
          const errorMessage =
            error.response?.data?.detail ||
            error.response?.data?.non_field_errors?.[0] ||
            "فشل تسجيل الدخول. تحقق من البيانات.";

          set({ loading: false, error: errorMessage });
          return { success: false, error: errorMessage };
        }
      },

      register: async (username, email, password) => {
        set({ loading: true, error: null });
        try {
          await authAPI.register(username, email, password);
          set({ loading: false, error: null });
          return { success: true };
        } catch (error) {
          const errorData = error.response?.data;
          let errorMessage = "فشل إنشاء الحساب.";

          if (errorData) {
            if (errorData.email) {
              errorMessage = `البريد الإلكتروني: ${errorData.email[0]}`;
            } else if (errorData.username) {
              errorMessage = `اسم المستخدم: ${errorData.username[0]}`;
            } else if (errorData.password) {
              errorMessage = `كلمة المرور: ${errorData.password[0]}`;
            } else if (errorData.detail) {
              errorMessage = errorData.detail;
            }
          }

          set({ loading: false, error: errorMessage });
          return { success: false, error: errorMessage };
        }
      },

      logout: async () => {
        set({ loading: true });
        try {
          const { refreshToken } = get();
          if (refreshToken) {
            await authAPI.logout(refreshToken);
          }
        } catch {
          // نكمل حتى لو فشل الـ logout على السيرفر
        } finally {
          tokenUtils.clearTokens();
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            loading: false,
            error: null,
          });
        }
      },

      fetchMe: async () => {
        set({ loading: true });
        try {
          const user = await authAPI.getMe();
          set({ user, loading: false });
          return user;
        } catch {
          set({ loading: false });
          return null;
        }
      },

      clearError: () => set({ error: null }),

      initializeAuth: async () => {
        const accessToken = tokenUtils.getAccessToken();
        const refreshToken = tokenUtils.getRefreshToken();

        if (!accessToken || !refreshToken) {
          set({ isAuthenticated: false, user: null });
          return;
        }

        set({ accessToken, refreshToken, isAuthenticated: true });
        await get().fetchMe();
      },
    }),
    {
      name: "efootball-auth",
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
        user: state.user,
      }),
    }
  )
);

export default useAuthStore;