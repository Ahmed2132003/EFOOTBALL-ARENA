import axiosInstance from "./axios";

export const userAPI = {
  async getMyProfile() {
    const response = await axiosInstance.get("/users/profile/");
    return response.data;
  },

  async getUserProfile(username) {
    const response = await axiosInstance.get(`/users/profile/${username}/`);
    return response.data;
  },

  async updateProfile(formData) {
    const response = await axiosInstance.patch("/users/profile/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },

  async changePassword(data) {
    const response = await axiosInstance.post("/users/change-password/", data);
    return response.data;
  },
};