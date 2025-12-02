import apiClient from '../utils/axios';

export const gamesAPI = {
  async createGame(data) {
    const response = await apiClient.post('/games', data);
    return response.data;
  },

  async getGames() {
    const response = await apiClient.get('/games');
    return response.data;
  },

  async getGame(gameId) {
    const response = await apiClient.get(`/games/${gameId}`);
    return response.data;
  },

  async joinGame(gameId) {
    const response = await apiClient.post(`/games/${gameId}/join`);
    return response.data;
  },

  async startGame(gameId) {
    const response = await apiClient.post(`/games/${gameId}/start`);
    return response.data;
  },

  async makeMove(gameId, articleTitle) {
    const response = await apiClient.post(`/games/${gameId}/move`, {
      article_title: articleTitle
    });
    return response.data;
  },

  async getAvailableLinks(gameId) {
    const response = await apiClient.get(`/games/${gameId}/available-links`);
    return response.data;
  },

  async getRandomArticles() {
    const response = await apiClient.get('/games/random-articles');
    return response.data;
  }
};