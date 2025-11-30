<script>
  import { push } from 'svelte-spa-router';
  import apiClient from '../lib/utils/axios';
  import { setUser } from '../lib/stores/auth';

  let username = '';
  let password = '';
  let error = '';
  let loading = false;

  async function handleLogin() {
    error = '';
    loading = true;

    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const response = await apiClient.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      
      const userResponse = await apiClient.get('/users/me');
      setUser(userResponse.data);
      
      push('/');
    } catch (err) {
      error = err.response?.data?.detail || 'Неверные учетные данные';
    } finally {
      loading = false;
    }
  }
</script>

<div class="login-page">
  <div class="login-container card">
    <div class="login-header">
      <span class="emoji">👋</span>
      <h1>Вход в WikiRush</h1>
      <p>Рады видеть тебя снова!</p>
    </div>

    {#if error}
      <div class="error-message">
        <span>⚠️</span>
        {error}
      </div>
    {/if}

    <form on:submit|preventDefault={handleLogin}>
      <div class="form-group">
        <label for="username">Имя пользователя</label>
        <input 
          id="username"
          type="text" 
          bind:value={username} 
          placeholder="Введите имя пользователя"
          required
          disabled={loading}
        />
      </div>

      <div class="form-group">
        <label for="password">Пароль</label>
        <input 
          id="password"
          type="password" 
          bind:value={password} 
          placeholder="Введите пароль"
          required
          disabled={loading}
        />
      </div>

      <button type="submit" class="btn btn-primary btn-block" disabled={loading}>
        {loading ? 'Вход...' : 'Войти'}
      </button>
    </form>

    <div class="divider">или</div>

    <p class="register-link">
      Нет аккаунта? <a href="#/register">Зарегистрироваться</a>
    </p>
  </div>
</div>

<style>
  .login-page {
    min-height: calc(100vh - 200px);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .login-container {
    max-width: 450px;
    width: 100%;
    padding: 40px;
  }

  .login-header {
    text-align: center;
    margin-bottom: 30px;
  }

  .login-header .emoji {
    font-size: 3rem;
    display: block;
    margin-bottom: 15px;
  }

  .login-header h1 {
    font-size: 2rem;
    margin-bottom: 10px;
    color: var(--text-dark);
  }

  .login-header p {
    color: var(--text-light);
  }

  .error-message {
    background: var(--light-pink);
    border: 2px solid var(--error);
    color: var(--error);
    padding: 12px 16px;
    border-radius: 10px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .form-group {
    margin-bottom: 20px;
  }

  label {
    display: block;
    margin-bottom: 8px;
    color: var(--text-dark);
    font-weight: 500;
  }

  .btn-block {
    width: 100%;
    margin-top: 10px;
  }

  .divider {
    text-align: center;
    margin: 25px 0;
    color: var(--text-light);
    position: relative;
  }

  .divider::before,
  .divider::after {
    content: '';
    position: absolute;
    top: 50%;
    width: 40%;
    height: 1px;
    background: var(--secondary-pink);
  }

  .divider::before {
    left: 0;
  }

  .divider::after {
    right: 0;
  }

  .register-link {
    text-align: center;
    color: var(--text-light);
  }

  .register-link a {
    color: var(--primary-pink);
    font-weight: 600;
    text-decoration: none;
  }

  .register-link a:hover {
    text-decoration: underline;
  }
</style>