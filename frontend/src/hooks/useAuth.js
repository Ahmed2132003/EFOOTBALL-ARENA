import { useCallback } from "react";
import { useNavigate } from "react-router-dom";
import useAuthStore from "../store/authStore";

const useAuth = () => {
  const navigate = useNavigate();
  const {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    loading,
    error,
    login,
    register,
    logout,
    fetchMe,
    clearError,
  } = useAuthStore();

  const handleLogin = useCallback(
    async (username, password) => {
      const result = await login(username, password);
      if (result.success) {
        navigate("/dashboard");
      }
      return result;
    },
    [login, navigate]
  );

  const handleRegister = useCallback(
    async (username, email, password, passwordConfirm) => {
      const result = await register(username, email, password, passwordConfirm);
      if (result.success) {
        navigate("/dashboard");
      }
      return result;
    },
    [register, navigate]
  );

  const handleLogout = useCallback(async () => {
    await logout();
    navigate("/login");
  }, [logout, navigate]);

  return {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    loading,
    error,
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    fetchMe,
    clearError,
  };
};

export default useAuth;