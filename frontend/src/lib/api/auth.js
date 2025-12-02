import apiClient from '../utils/axios';

export const authAPI = {
  async register(username, email, password) {
    // Попробуем отправить данные точно в том формате, который ожидает бэкенд
    const response = await apiClient.post('/auth/register', {
      username: username.trim(),  // Убираем пробелы
      email: email.trim().toLowerCase(),  // Приводим email к нижнему регистру
      password: password
    });
    return response.data;
  },

  async login(username, password) {
    const formData = new FormData();
    formData.append('username', username.trim());
    formData.append('password', password);

    const response = await apiClient.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data;
  },

  async getCurrentUser() {
    const response = await apiClient.get('/users/me');
    return response.data;
  }
};