<script>
  import { push } from 'svelte-spa-router';
  import apiClient from '../lib/utils/axios';
  import { setUser } from '../lib/stores/auth';

  let username = '';
  let email = '';
  let password = '';
  let confirmPassword = '';
  let error = '';
  let loading = false;

  async function handleRegister() {
    error = '';

    if (password !== confirmPassword) {
      error = 'Пароли не совпадают';
      return;
    }

    if (password.length < 6) {
      error = 'Пароль должен быть не менее 6 символов';
      return;
    }

    loading = true;

    try {
      await apiClient.post('/auth/register', {
        username,
        email,
        password
      });

      // Автоматический вход после регистрации
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const loginResponse = await apiClient.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      localStorage.setItem('access_token', loginResponse.data.access_token);
      localStorage.setItem('refresh_token', loginResponse.data.refresh_token);
      
      const userResponse = await apiClient.get('/users/me');
      setUser(userResponse.data);
      
      push('/');
    } catch (err) {
      // ИСПРАВЛЕНИЕ: правильная обработка ошибок
      console.error('Ошибка регистрации:', err);
      
      if (err.response) {
        // Ошибка от сервера
        if (err.response.data && err.response.data.detail) {
          // Если detail это строка
          if (typeof err.response.data.detail === 'string') {
            error = err.response.data.detail;
          } 
          // Если detail это массив (валидация Pydantic)
          else if (Array.isArray(err.response.data.detail)) {
            error = err.response.data.detail.map(e => e.msg).join(', ');
          } 
          // Если detail это объект
          else {
            error = JSON.stringify(err.response.data.detail);
          }
        } else {
          error = 'Ошибка регистрации: ' + err.response.status;
        }
      } else if (err.request) {
        // Запрос был отправлен, но ответа не получено
        error = 'Сервер не отвечает. Проверьте, что бэкенд запущен.';
      } else {
        // Что-то пошло не так при настройке запроса
        error = 'Ошибка: ' + err.message;
      }
    } finally {
      loading = false;
    }
  }
</script>

<div class="register-page">
  <div class="register-container card">
    <div class="register-header">
      <span class="emoji">🎮</span>
      <h1>Регистрация</h1>
      <p>Присоединяйся к WikiRush!</p>
    </div>

    {#if error}
      <div class="error-message">
        <span>⚠️</span>
        {error}
      </div>
    {/if}

    <form on:submit|preventDefault={handleRegister}>
      <div class="form-group">
        <label for="username">Имя пользователя</label>
        <input 
          id="username"
          type="text" 
          bind:value={username} 
          placeholder="Выберите имя пользователя"
          required
          disabled={loading}
        />
      </div>

      <div class="form-group">
        <label for="email">Email</label>
        <input 
          id="email"
          type="email" 
          bind:value={email} 
          placeholder="Введите email"
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
          placeholder="Минимум 6 символов"
          required
          disabled={loading}
        />
      </div>

      <div class="form-group">
        <label for="confirmPassword">Подтвердите пароль</label>
        <input 
          id="confirmPassword"
          type="password" 
          bind:value={confirmPassword} 
          placeholder="Повторите пароль"
          required
          disabled={loading}
        />
      </div>

      <button type="submit" class="btn btn-primary btn-block" disabled={loading}>
        {loading ? 'Регистрация...' : 'Создать аккаунт'}
      </button>
    </form>

    <div class="divider">или</div>

    <p class="login-link">
      Уже есть аккаунт? <a href="#/login">Войти</a>
    </p>
  </div>
</div>

<style>
  .register-page {
    min-height: calc(100vh - 200px);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .register-container {
    max-width: 450px;
    width: 100%;
    padding: 40px;
  }

  .register-header {
    text-align: center;
    margin-bottom: 30px;
  }

  .register-header .emoji {
    font-size: 3rem;
    display: block;
    margin-bottom: 15px;
  }

  .register-header h1 {
    font-size: 2rem;
    margin-bottom: 10px;
    color: var(--text-dark);
  }

  .register-header p {
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
    word-break: break-word;
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

  .login-link {
    text-align: center;
    color: var(--text-light);
  }

  .login-link a {
    color: var(--primary-pink);
    font-weight: 600;
    text-decoration: none;
  }

  .login-link a:hover {
    text-decoration: underline;
  }
</style>