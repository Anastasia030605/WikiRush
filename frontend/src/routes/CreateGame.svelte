<script>
  import { onMount } from 'svelte';
  import { push } from 'svelte-spa-router';
  import { gamesAPI } from '../lib/api/games';
  import { isAuthenticated } from '../lib/stores/auth';

  let mode = 'multiplayer';
  let useRandomArticles = true;
  let startArticle = '';
  let targetArticle = '';
  let maxPlayers = 4;
  let loading = false;
  let error = '';
  let loadingRandom = false;

  onMount(() => {
    if (!$isAuthenticated) {
      push('/login');
    }
  });

  async function getRandomArticles() {
    try {
      loadingRandom = true;
      const data = await gamesAPI.getRandomArticles();
      startArticle = data.start_article;
      targetArticle = data.target_article;
    } catch (err) {
      console.error('Ошибка получения случайных статей:', err);
      error = 'Не удалось получить случайные статьи';
    } finally {
      loadingRandom = false;
    }
  }

  async function handleSubmit() {
    error = '';
    
    if (!useRandomArticles && (!startArticle || !targetArticle)) {
      error = 'Заполните начальную и целевую статьи';
      return;
    }

    loading = true;

    try {
      const gameData = {
        mode,
        max_players: mode === 'multiplayer' ? maxPlayers : 1
      };

      if (useRandomArticles) {
        gameData.use_random_articles = true;
      } else {
        gameData.start_article = startArticle;
        gameData.target_article = targetArticle;
      }

      const game = await gamesAPI.createGame(gameData);
      push(`/games/${game.id}`);
    } catch (err) {
      console.error('Ошибка создания игры:', err);
      
      if (err.response && err.response.data && err.response.data.detail) {
        if (typeof err.response.data.detail === 'string') {
          error = err.response.data.detail;
        } else {
          error = JSON.stringify(err.response.data.detail);
        }
      } else {
        error = 'Не удалось создать игру';
      }
    } finally {
      loading = false;
    }
  }
</script>

<div class="create-game-page">
  <div class="create-game-container card">
    <div class="page-header">
      <h1>🎮 Создать новую игру</h1>
      <p>Настрой параметры и начни играть!</p>
    </div>

    {#if error}
      <div class="error-message">
        <span>⚠️</span>
        {error}
      </div>
    {/if}

    <form on:submit|preventDefault={handleSubmit}>
      <div class="form-section">
        <h3>Режим игры</h3>
        <div class="mode-options">
          <label class="mode-option" class:selected={mode === 'single'}>
            <input type="radio" bind:group={mode} value="single" />
            <div class="mode-content">
              <span class="emoji">🧑</span>
              <span class="mode-name">Одиночный</span>
              <span class="mode-desc">Играй в своём темпе</span>
            </div>
          </label>

          <label class="mode-option" class:selected={mode === 'multiplayer'}>
            <input type="radio" bind:group={mode} value="multiplayer" />
            <div class="mode-content">
              <span class="emoji">👥</span>
              <span class="mode-name">Мультиплеер</span>
              <span class="mode-desc">Соревнуйся с друзьями</span>
            </div>
          </label>
        </div>
      </div>

      {#if mode === 'multiplayer'}
        <div class="form-group">
          <label for="maxPlayers">Максимум игроков</label>
          <input 
            id="maxPlayers"
            type="number" 
            bind:value={maxPlayers}
            min="2"
            max="10"
            required
          />
        </div>
      {/if}

      <div class="form-section">
        <h3>Статьи</h3>
        <div class="toggle-option">
          <label>
            <input type="checkbox" bind:checked={useRandomArticles} />
            <span>Использовать случайные статьи</span>
          </label>
        </div>

        {#if useRandomArticles}
          <div class="random-preview">
            {#if loadingRandom}
              <div class="loading-mini">Загрузка...</div>
            {:else if startArticle && targetArticle}
              <div class="preview-articles">
                <div class="preview-article">
                  <span class="label">📖 От:</span>
                  <span class="value">{startArticle}</span>
                </div>
                <div class="preview-article">
                  <span class="label">🎯 До:</span>
                  <span class="value">{targetArticle}</span>
                </div>
              </div>
            {/if}
            <button 
              type="button" 
              class="btn btn-outline" 
              on:click={getRandomArticles}
              disabled={loadingRandom}
            >
              🎲 Предпросмотр случайных статей
            </button>
          </div>
        {:else}
          <div class="manual-articles">
            <div class="form-group">
              <label for="startArticle">📖 Начальная статья</label>
              <input 
                id="startArticle"
                type="text" 
                bind:value={startArticle}
                placeholder="Например: Россия"
                required={!useRandomArticles}
              />
            </div>

            <div class="form-group">
              <label for="targetArticle">🎯 Целевая статья</label>
              <input 
                id="targetArticle"
                type="text" 
                bind:value={targetArticle}
                placeholder="Например: Физика"
                required={!useRandomArticles}
              />
            </div>
          </div>
        {/if}
      </div>

      <div class="form-actions">
        <button type="button" class="btn btn-outline" on:click={() => push('/games')}>
          Отмена
        </button>
        <button type="submit" class="btn btn-primary" disabled={loading}>
          {loading ? 'Создание...' : '🚀 Создать игру'}
        </button>
      </div>
    </form>
  </div>
</div>

<style>
  .create-game-page {
    max-width: 700px;
    margin: 0 auto;
  }

  .create-game-container {
    padding: 40px;
  }

  .page-header {
    text-align: center;
    margin-bottom: 40px;
  }

  .page-header h1 {
    font-size: 2.2rem;
    margin-bottom: 10px;
    color: var(--text-dark);
  }

  .page-header p {
    color: var(--text-light);
    font-size: 1.1rem;
  }

  .error-message {
    background: var(--light-pink);
    border: 2px solid var(--error);
    color: var(--error);
    padding: 12px 16px;
    border-radius: 10px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .form-section {
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 2px solid var(--light-pink);
  }

  .form-section:last-of-type {
    border-bottom: none;
  }

  .form-section h3 {
    margin-bottom: 16px;
    color: var(--text-dark);
    font-size: 1.3rem;
  }

  .mode-options {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }

  .mode-option {
    cursor: pointer;
    padding: 20px;
    border: 3px solid var(--secondary-pink);
    border-radius: 15px;
    transition: all 0.3s ease;
    background: white;
  }

  .mode-option:hover {
    border-color: var(--primary-pink);
    transform: translateY(-3px);
  }

  .mode-option.selected {
    border-color: var(--primary-pink);
    background: linear-gradient(135deg, var(--light-pink), var(--light-green));
  }

  .mode-option input[type="radio"] {
    display: none;
  }

  .mode-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    text-align: center;
  }

  .mode-content .emoji {
    font-size: 2.5rem;
  }

  .mode-name {
    font-weight: 700;
    font-size: 1.1rem;
    color: var(--text-dark);
  }

  .mode-desc {
    font-size: 0.9rem;
    color: var(--text-light);
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

  .toggle-option {
    margin-bottom: 20px;
  }

  .toggle-option label {
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
  }

  .toggle-option input[type="checkbox"] {
    width: auto;
    cursor: pointer;
  }

  .random-preview {
    background: var(--light-green);
    padding: 20px;
    border-radius: 12px;
    text-align: center;
  }

  .loading-mini {
    color: var(--text-light);
    margin-bottom: 16px;
  }

  .preview-articles {
    margin-bottom: 16px;
  }

  .preview-article {
    display: flex;
    justify-content: space-between;
    padding: 12px;
    background: white;
    border-radius: 8px;
    margin-bottom: 10px;
  }

  .preview-article .label {
    font-weight: 600;
    color: var(--text-light);
  }

  .preview-article .value {
    font-weight: 600;
    color: var(--text-dark);
  }

  .manual-articles {
    margin-top: 20px;
  }

  .form-actions {
    display: flex;
    gap: 16px;
    justify-content: flex-end;
    margin-top: 32px;
  }

  .form-actions button {
    padding: 12px 28px;
  }
</style>