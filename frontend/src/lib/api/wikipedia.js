import apiClient from '../utils/axios';

export const wikipediaAPI = {
  async getArticleSummary(title) {
    const response = await apiClient.get(`/wikipedia/article/${encodeURIComponent(title)}/summary`);
    return response.data;
  },

  async getArticleLinks(title) {
    const response = await apiClient.get(`/wikipedia/article/${encodeURIComponent(title)}/links`);
    return response.data;
  },

  async searchArticles(query) {
    const response = await apiClient.get(`/wikipedia/search`, {
      params: { query }
    });
    return response.data;
  }
};