<script>
  import apiClient from '../lib/utils/axios';

  let result = '';
  let error = '';

  async function testConnection() {
    result = '';
    error = '';
    
    try {
      const response = await fetch('http://localhost:8000/docs');
      result = 'Бэкенд доступен! Статус: ' + response.status;
    } catch (err) {
      error = 'Ошибка подключения: ' + err.message;
    }
  }

  async function testRegister() {
    result = '';
    error = '';
    
    try {
      // Генерируем уникальный email для каждого теста
      const timestamp = Date.now();
      const response = await apiClient.post('/auth/register', {
        username: 'test_user_' + timestamp,
        email: 'test_' + timestamp + '@example.com',  // ← Уникальный email
        password: '123456'
      });
      result = 'Регистрация успешна! ' + JSON.stringify(response.data);
    } catch (err) {
      console.error('Ошибка:', err);
      if (err.response) {
        error = 'Ошибка от сервера: ' + JSON.stringify(err.response.data);
      } else if (err.request) {
        error = 'Сервер не отвечает. Проверьте, что бэкенд запущен на порту 8000';
      } else {
        error = 'Ошибка: ' + err.message;
      }
    }
  }
</script>

<!-- Остальной код остается без изменений -->

<div class="test-page">
  <div class="card">
    <h1>🔧 Тест подключения к бэкенду</h1>
    
    <div class="test-info">
      <p><strong>URL бэкенда:</strong> http://localhost:8000/api/v1</p>
      <p><strong>URL фронтенда:</strong> http://localhost:5173</p>
    </div>

    <div class="buttons">
      <button class="btn btn-primary" on:click={testConnection}>
        Проверить доступность бэкенда
      </button>
      <button class="btn btn-secondary" on:click={testRegister}>
        Тест регистрации
      </button>
    </div>

    {#if result}
      <div class="success-message">
        ✅ {result}
      </div>
    {/if}

    {#if error}
      <div class="error-message">
        ⚠️ {error}
      </div>
    {/if}

    <div class="instructions">
      <h3>Как проверить подключение:</h3>
      <ol>
        <li>Убедитесь, что бэкенд запущен (откройте http://localhost:8000/docs)</li>
        <li>Нажмите "Проверить доступность бэкенда"</li>
        <li>Если успешно - нажмите "Тест регистрации"</li>
        <li>Откройте Console (F12) и посмотрите детали ошибок</li>
      </ol>
    </div>
  </div>
</div>

<style>
  .test-page {
    max-width: 800px;
    margin: 40px auto;
    padding: 20px;
  }

  .test-info {
    background: var(--light-green);
    padding: 16px;
    border-radius: 12px;
    margin: 20px 0;
  }

  .test-info p {
    margin: 8px 0;
  }

  .buttons {
    display: flex;
    gap: 16px;
    margin: 20px 0;
  }

  .success-message {
    background: var(--light-green);
    border: 2px solid var(--success);
    color: var(--success);
    padding: 16px;
    border-radius: 12px;
    margin: 20px 0;
  }

  .error-message {
    background: var(--light-pink);
    border: 2px solid var(--error);
    color: var(--error);
    padding: 16px;
    border-radius: 12px;
    margin: 20px 0;
    word-break: break-word;
  }

  .instructions {
    background: var(--light-pink);
    padding: 20px;
    border-radius: 12px;
    margin-top: 30px;
  }

  .instructions h3 {
    margin-bottom: 12px;
  }

  .instructions ol {
    margin-left: 20px;
  }

  .instructions li {
    margin: 8px 0;
  }
</style>