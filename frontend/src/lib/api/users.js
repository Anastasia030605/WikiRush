import apiClient from '../utils/axios';

export const usersAPI = {
  async getUser(userId) {
    const response = await apiClient.get(`/users/${userId}`);
    return response.data;
  },

  async getUserStats(userId) {
    const response = await apiClient.get(`/users/${userId}/stats`);
    return response.data;
  },

  async getLeaderboard() {
    const response = await apiClient.get('/leaderboard');
    return response.data;
  }
};