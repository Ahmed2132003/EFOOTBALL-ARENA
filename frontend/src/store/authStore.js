import { create } from "zustand";
import { persist } from "zustand/middleware";
import { authAPI } from "../api/auth.api";
import { userAPI } from "../api/user.api";
import { tokenUtils } from "../utils/token";

const getFirstError = (value) => {
  if (Array.isArray(value)) return value[0];
  if (typeof value === "string") return value;
  return null;
};

const getApiErrorMessage = (error, fallbackMessage) => {
  const errorData = error.response?.data;
  if (!errorData) {
    return error.request
      ? "تعذر الاتصال بالسيرفر. تأكد أن الباك إند يعمل على localhost:8765."
      : fallbackMessage;
  }
  const fields = [
    "detail", "non_field_errors", "username", "email",
    "password", "password_confirm", "current_password",
    "new_password", "confirm_password", "error",
  ];
  for (const field of fields) {
    const message = getFirstError(errorData[field]);
    if (message) return message;
  }
  return fallbackMessage;
};

const readTokens = (data) => ({
  access:  data?.tokens?.access  || data?.access,
  refresh: data?.tokens?.refresh || data?.refresh,
});

const useAuthStore = create(
  persist(
    (set, get) => ({
      user:            null,
      profile:         null,
      accessToken:     null,
      refreshToken:    null,
      isAuthenticated: false,
      loading:         false,
      profileLoading:  false,
      passwordLoading: false,
      error:           null,

      setTokens: (accessToken, refreshToken) => {
        tokenUtils.setTokens(accessToken, refreshToken);
        set({ accessToken, refreshToken });
      },

      login: async (username, password) => {
        set({ loading: true, error: null });
        try {
          const data = await authAPI.login(username, password);
          const { access, refresh } = readTokens(data);
          if (!access || !refresh) throw new Error("Missing tokens in login response.");

          tokenUtils.setTokens(access, refresh);
          set({
            user: data.user || null, accessToken: access,
            refreshToken: refresh, isAuthenticated: true,
            loading: false, error: null,
          });
          if (!data.user) await get().fetchMe();
          return { success: true };
        } catch (error) {
          tokenUtils.clearTokens();
          const errorMessage = getApiErrorMessage(error, "فشل تسجيل الدخول.");
          set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false, loading: false, error: errorMessage });
          return { success: false, error: errorMessage };
        }
      },

      register: async (username, email, password, passwordConfirm) => {
        set({ loading: true, error: null });
        try {
          const data = await authAPI.register(username, email, password, passwordConfirm);
          const { access, refresh } = readTokens(data);
          if (!access || !refresh) throw new Error("Missing tokens in register response.");

          tokenUtils.setTokens(access, refresh);
          set({
            user: data.user || null, accessToken: access,
            refreshToken: refresh, isAuthenticated: true,
            loading: false, error: null,
          });
          if (!data.user) await get().fetchMe();
          return { success: true };
        } catch (error) {
          tokenUtils.clearTokens();
          const rawMessage = getApiErrorMessage(error, "فشل إنشاء الحساب.");
          const fieldLabels = { email: "البريد الإلكتروني", username: "اسم المستخدم", password: "كلمة المرور", password_confirm: "تأكيد كلمة المرور" };
          const errorData = error.response?.data || {};
          const fieldName = Object.keys(fieldLabels).find((f) => errorData[f]);
          const errorMessage = fieldName
            ? `${fieldLabels[fieldName]}: ${getFirstError(errorData[fieldName])}`
            : rawMessage;
          set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false, loading: false, error: errorMessage });
          return { success: false, error: errorMessage };
        }
      },

      logout: async () => {
        set({ loading: true });
        try {
          const { refreshToken } = get();
          if (refreshToken) await authAPI.logout(refreshToken);
        } catch (_) {}
        finally {
          tokenUtils.clearTokens();
          set({ user: null, profile: null, accessToken: null, refreshToken: null, isAuthenticated: false, loading: false, error: null });
        }
      },

      fetchMe: async () => {
        set({ loading: true });
        try {
          const data = await authAPI.getMe();
          const user = data.user || data;
          set({ user, loading: false, isAuthenticated: true });
          return user;
        } catch (_) {
          tokenUtils.clearTokens();
          set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false, loading: false });
          return null;
        }
      },

      fetchProfile: async () => {
        set({ profileLoading: true });
        try {
          const data = await userAPI.getMyProfile();
          const profile = data.profile || data;
          set({ profile, profileLoading: false });
          return profile;
        } catch (error) {
          set({ profileLoading: false });
          return null;
        }
      },

      updateProfile: async (formData) => {
        set({ profileLoading: true });
        try {
          const data = await userAPI.updateProfile(formData);
          const profile = data.profile || data;
          // sync avatar into user object too
          set((state) => ({
            profile,
            profileLoading: false,
            user: state.user
              ? { ...state.user, avatar: profile.avatar_url || state.user.avatar }
              : state.user,
          }));
          return { success: true, profile };
        } catch (error) {
          const errorMessage = getApiErrorMessage(error, "فشل تحديث الملف الشخصي.");
          set({ profileLoading: false });
          return { success: false, error: errorMessage };
        }
      },

      changePassword: async (data) => {
        set({ passwordLoading: true });
        try {
          await userAPI.changePassword(data);
          set({ passwordLoading: false });
          return { success: true };
        } catch (error) {
          const errorMessage = getApiErrorMessage(error, "فشل تغيير كلمة المرور.");
          set({ passwordLoading: false });
          return { success: false, error: errorMessage };
        }
      },

      clearError: () => set({ error: null }),

      initializeAuth: async () => {
        const accessToken  = tokenUtils.getAccessToken();
        const refreshToken = tokenUtils.getRefreshToken();
        if (!accessToken || !refreshToken) {
          set({ accessToken: null, refreshToken: null, isAuthenticated: false, user: null });
          return;
        }
        set({ accessToken, refreshToken, isAuthenticated: true });
        await get().fetchMe();
      },
    }),
    {
      name: "efootball-auth",
      partialize: (state) => ({
        accessToken:     state.accessToken,
        refreshToken:    state.refreshToken,
        isAuthenticated: state.isAuthenticated,
        user:            state.user,
      }),
    }
  )
);

export default useAuthStore;