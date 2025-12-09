<script>
  import { onMount } from 'svelte';
  import { user } from '../lib/stores/auth';
  import apiClient from '../lib/utils/axios';

  let currentUser = null;
  let stats = null;
  let achievements = [];
  let loading = true;
  let error = '';
  let uploadingAvatar = false;
  let fileInput;

  // Subscribe to user store and reload profile when user changes
  user.subscribe(async (value) => {
    currentUser = value;
    if (currentUser) {
      await loadProfile();
    }
  });

  onMount(async () => {
    if (currentUser) {
      await loadProfile();
    }
  });

  async function loadProfile() {
    loading = true;
    error = '';

    try {
      // Load stats
      const statsResponse = await apiClient.get(`/users/${currentUser.id}/stats`);
      stats = statsResponse.data;

      // Load achievements
      const achievementsResponse = await apiClient.get(`/users/${currentUser.id}/achievements`);
      achievements = achievementsResponse.data;
    } catch (err) {
      console.error('Error loading profile:', err);
      error = err.response?.data?.detail || 'Failed to load profile';
    } finally {
      loading = false;
    }
  }

  function formatTime(seconds) {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  function triggerFileInput() {
    fileInput.click();
  }

  async function handleAvatarUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Проверка размера файла (5MB)
    if (file.size > 5 * 1024 * 1024) {
      error = 'Размер файла не должен превышать 5MB';
      return;
    }

    // Проверка типа файла
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      error = 'Разрешены только изображения (JPEG, PNG, GIF, WebP)';
      return;
    }

    uploadingAvatar = true;
    error = '';

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await apiClient.post('/users/me/avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Обновляем аватар пользователя
      currentUser.avatar_url = response.data.avatar_url;
      user.set(currentUser);
    } catch (err) {
      console.error('Error uploading avatar:', err);
      error = err.response?.data?.detail || 'Ошибка при загрузке аватара';
    } finally {
      uploadingAvatar = false;
    }
  }
</script>

<div class="profile-container">
  <div class="profile-header">
    <div class="user-info">
      <div class="avatar-container">
        <div class="avatar" on:click={triggerFileInput}>
          {#if currentUser?.avatar_url}
            <img src={`http://localhost:8000${currentUser.avatar_url}`} alt="Avatar" />
          {:else}
            <span>{currentUser?.username?.charAt(0).toUpperCase()}</span>
          {/if}
          <div class="avatar-overlay">
            {#if uploadingAvatar}
              <span>Загрузка...</span>
            {:else}
              <span>📷</span>
            {/if}
          </div>
        </div>
        <input
          type="file"
          bind:this={fileInput}
          on:change={handleAvatarUpload}
          accept="image/jpeg,image/png,image/gif,image/webp"
          style="display: none;"
        />
      </div>
      <div class="user-details">
        <h1>{currentUser?.username}</h1>
        <p class="email">{currentUser?.email}</p>
      </div>
    </div>
  </div>

  {#if !currentUser}
    <div class="loading">Загрузка профиля...</div>
  {:else if loading}
    <div class="loading">Загрузка...</div>
  {:else if error}
    <div class="error">{error}</div>
  {:else}
    <!-- Statistics Section -->
    <section class="stats-section">
      <h2>Статистика</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">🎮</div>
          <div class="stat-value">{stats?.total_games || 0}</div>
          <div class="stat-label">Всего игр</div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">🏆</div>
          <div class="stat-value">{stats?.total_wins || 0}</div>
          <div class="stat-label">Побед</div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-value">{stats?.win_rate || 0}%</div>
          <div class="stat-label">Процент побед</div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">⚡</div>
          <div class="stat-value">{formatTime(stats?.best_time)}</div>
          <div class="stat-label">Лучшее время</div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">👣</div>
          <div class="stat-value">{stats?.best_steps || 'N/A'}</div>
          <div class="stat-label">Лучший результат</div>
        </div>
      </div>
    </section>

    <!-- Achievements Section -->
    <section class="achievements-section">
      <h2>Достижения ({achievements.length})</h2>
      {#if achievements.length === 0}
        <div class="no-achievements">
          <p>У вас пока нет достижений</p>
          <p>Играйте в WikiRush, чтобы получить первые награды!</p>
        </div>
      {:else}
        <div class="achievements-grid">
          {#each achievements as achievement}
            <div class="achievement-card">
              <div class="achievement-icon">{achievement.achievement_icon}</div>
              <div class="achievement-content">
                <h3>{achievement.achievement_name}</h3>
                <p>{achievement.achievement_description}</p>
                <div class="achievement-meta">
                  <span class="category">{achievement.achievement_category}</span>
                  <span class="points">{achievement.achievement_points} очков</span>
                  <span class="date">{formatDate(achievement.unlocked_at)}</span>
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </section>
  {/if}
</div>

<style>
  .profile-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 20px;
  }

  .profile-header {
    background: linear-gradient(135deg, #d91e6e 0%, #8b2b8b 100%);
    border-radius: 20px;
    padding: 40px;
    margin-bottom: 40px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 30px;
  }

  .avatar-container {
    position: relative;
  }

  .avatar {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
    font-weight: bold;
    color: #d91e6e;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    cursor: pointer;
    position: relative;
    overflow: hidden;
    transition: transform 0.3s ease;
  }

  .avatar:hover {
    transform: scale(1.05);
  }

  .avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .avatar-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s ease;
    border-radius: 50%;
    font-size: 2rem;
  }

  .avatar:hover .avatar-overlay {
    opacity: 1;
  }

  .user-details h1 {
    margin: 0;
    font-size: 2.5rem;
    color: white;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  }

  .email {
    margin: 5px 0 0;
    color: white;
    font-size: 1.1rem;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
  }

  .stats-section, .achievements-section {
    background: white;
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 40px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  }

  .stats-section h2, .achievements-section h2 {
    margin: 0 0 30px 0;
    font-size: 2rem;
    color: #1a1a1a;
    font-weight: 700;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
  }

  .stat-card {
    background: linear-gradient(135deg, #fce4ec 0%, #f8bbd0 100%);
    border-radius: 15px;
    padding: 25px;
    text-align: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border: 2px solid #f48fb1;
  }

  .stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(217, 30, 110, 0.3);
  }

  .stat-icon {
    font-size: 3rem;
    margin-bottom: 10px;
  }

  .stat-value {
    font-size: 2.5rem;
    font-weight: bold;
    color: #c2185b;
    margin: 10px 0;
  }

  .stat-label {
    font-size: 0.95rem;
    color: #424242;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .achievements-grid {
    display: grid;
    gap: 20px;
  }

  .achievement-card {
    display: flex;
    align-items: flex-start;
    gap: 20px;
    padding: 20px;
    background: linear-gradient(135deg, #fff0f3 0%, #fce4ec 100%);
    border-radius: 15px;
    border-left: 5px solid #d91e6e;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .achievement-card:hover {
    transform: translateX(5px);
    box-shadow: 0 4px 15px rgba(217, 30, 110, 0.2);
  }

  .achievement-icon {
    font-size: 3rem;
    min-width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: white;
    border-radius: 15px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
  }

  .achievement-content {
    flex: 1;
  }

  .achievement-content h3 {
    margin: 0 0 8px 0;
    font-size: 1.3rem;
    color: #1a1a1a;
    font-weight: 700;
  }

  .achievement-content p {
    margin: 0 0 12px 0;
    color: #424242;
    line-height: 1.5;
  }

  .achievement-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    font-size: 0.85rem;
  }

  .category, .points, .date {
    padding: 6px 14px;
    border-radius: 20px;
    background: #f48fb1;
    color: white;
    font-weight: 600;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .no-achievements {
    text-align: center;
    padding: 60px 20px;
    color: var(--text-light);
  }

  .no-achievements p:first-child {
    font-size: 1.3rem;
    margin-bottom: 10px;
  }

  .loading, .error {
    text-align: center;
    padding: 40px;
    font-size: 1.2rem;
    color: var(--text-light);
  }

  .error {
    color: var(--error-red);
  }

  @media (max-width: 768px) {
    .user-info {
      flex-direction: column;
      text-align: center;
    }

    .stats-grid {
      grid-template-columns: 1fr;
    }

    .achievement-card {
      flex-direction: column;
      text-align: center;
    }

    .achievement-meta {
      justify-content: center;
    }
  }
</style>
