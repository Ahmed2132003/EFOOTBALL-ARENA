import axiosInstance from "./axios";

export const authAPI = {
  async login(email, password) {
    const response = await axiosInstance.post("/auth/login/", {
      email,
      password,
    });
    return response.data;
  },

  async register(username, email, password) {
    const response = await axiosInstance.post("/auth/register/", {
      username,
      email,
      password,
    });
    return response.data;
  },

  async logout(refreshToken) {
    const response = await axiosInstance.post("/auth/logout/", {
      refresh: refreshToken,
    });
    return response.data;
  },

  async refreshToken(refreshToken) {
    const response = await axiosInstance.post("/auth/token/refresh/", {
      refresh: refreshToken,
    });
    return response.data;
  },

  async getMe() {
    const response = await axiosInstance.get("/auth/me/");
    return response.data;
  },
};