<script>
  import { push } from 'svelte-spa-router';
  import apiClient from '../lib/utils/axios';

  let mode = 'single';
  let startArticle = '';
  let targetArticle = '';
  let maxSteps = 100;
  let timeLimit = 300;
  let maxPlayers = 10;
  let error = '';
  let loading = false;
  let generatingRandom = false;

  async function getRandomArticles() {
    generatingRandom = true;
    error = '';

    try {
      const response = await apiClient.get('/games/random-articles');
      startArticle = response.data.start_article;
      targetArticle = response.data.target_article;
    } catch (err) {
      console.error('Error getting random articles:', err);
      error = err.response?.data?.detail || 'Failed to get random articles';
    } finally {
      generatingRandom = false;
    }
  }

  async function handleCreateGame() {
    error = '';
    loading = true;

    try {
      const gameData = {
        mode,
        start_article: startArticle || null,
        target_article: targetArticle || null,
        max_steps: maxSteps,
        time_limit: timeLimit,
        max_players: mode === 'single' ? 1 : maxPlayers
      };

      const response = await apiClient.post('/games', gameData);
      const gameId = response.data.id;

      await apiClient.post(`/games/${gameId}/join`);

      // Auto-start single player games
      if (mode === 'single') {
        await apiClient.post(`/games/${gameId}/start`);
      }

      push(`/game/${gameId}`);
    } catch (err) {
      console.error('Create game error:', err);
      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          error = err.response.data.detail.map(e => e.msg).join(', ');
        } else if (typeof err.response.data.detail === 'object') {
          error = JSON.stringify(err.response.data.detail);
        } else {
          error = err.response.data.detail;
        }
      } else {
        error = err.message || 'Error creating game';
      }
    } finally {
      loading = false;
    }
  }
</script>

<div class="create-game-page">
  <div class="create-game-container card">
    <div class="header">
      <h1>Create Game</h1>
      <p>Configure your WikiRush game</p>
    </div>

    {#if error}
      <div class="error-message">
        <span>!</span>
        {error}
      </div>
    {/if}

    <form on:submit|preventDefault={handleCreateGame}>
      <div class="form-group">
        <label for="mode">Game Mode</label>
        <select id="mode" bind:value={mode} disabled={loading}>
          <option value="single">Single Player</option>
          <option value="multiplayer">Multiplayer</option>
          <option value="race">Race</option>
        </select>
      </div>

      <div class="articles-section">
        <div class="section-header">
          <h3>Wikipedia Articles</h3>
          <button
            type="button"
            class="btn btn-secondary btn-sm"
            on:click={getRandomArticles}
            disabled={generatingRandom || loading}
          >
            {generatingRandom ? 'Generating...' : 'Random Articles'}
          </button>
        </div>

        <div class="form-group">
          <label for="startArticle">Start Article</label>
          <input
            id="startArticle"
            type="text"
            bind:value={startArticle}
            placeholder="Article name (empty = random)"
            disabled={loading}
          />
        </div>

        <div class="form-group">
          <label for="targetArticle">Target Article</label>
          <input
            id="targetArticle"
            type="text"
            bind:value={targetArticle}
            placeholder="Article name (empty = random)"
            disabled={loading}
          />
        </div>
      </div>

      <div class="settings-row">
        <div class="form-group">
          <label for="maxSteps">Max Steps</label>
          <input
            id="maxSteps"
            type="number"
            bind:value={maxSteps}
            min="1"
            max="1000"
            disabled={loading}
          />
        </div>

        <div class="form-group">
          <label for="timeLimit">Time (sec)</label>
          <input
            id="timeLimit"
            type="number"
            bind:value={timeLimit}
            min="30"
            max="3600"
            disabled={loading}
          />
        </div>
      </div>

      {#if mode !== 'single'}
        <div class="form-group">
          <label for="maxPlayers">Max Players</label>
          <input
            id="maxPlayers"
            type="number"
            bind:value={maxPlayers}
            min="2"
            max="50"
            disabled={loading}
          />
        </div>
      {/if}

      <div class="buttons">
        <button type="submit" class="btn btn-primary btn-block" disabled={loading}>
          {loading ? 'Creating...' : 'Create Game'}
        </button>
        <button
          type="button"
          class="btn btn-outline btn-block"
          on:click={() => push('/games')}
          disabled={loading}
        >
          Cancel
        </button>
      </div>
    </form>
  </div>
</div>

<style>
  .create-game-page {
    min-height: calc(100vh - 200px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }

  .create-game-container {
    max-width: 600px;
    width: 100%;
    padding: 40px;
  }

  .header {
    text-align: center;
    margin-bottom: 30px;
  }

  .header h1 {
    font-size: 2rem;
    margin-bottom: 10px;
    color: var(--text-dark);
  }

  .header p {
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

  input, select {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid var(--secondary-pink);
    border-radius: 10px;
    font-size: 1rem;
    transition: all 0.3s ease;
  }

  input:focus, select:focus {
    outline: none;
    border-color: var(--primary-pink);
    box-shadow: 0 0 0 3px rgba(255, 105, 180, 0.1);
  }

  input:disabled, select:disabled {
    background: #f5f5f5;
    cursor: not-allowed;
  }

  .articles-section {
    background: var(--light-pink);
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
  }

  .section-header h3 {
    font-size: 1.2rem;
    color: var(--text-dark);
    margin: 0;
  }

  .settings-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
  }

  .buttons {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 30px;
  }

  .btn-block {
    width: 100%;
  }

  .btn-sm {
    padding: 8px 16px;
    font-size: 0.9rem;
  }

  .btn-outline {
    background: transparent;
    color: var(--primary-pink);
    border: 2px solid var(--primary-pink);
  }

  .btn-outline:hover {
    background: var(--light-pink);
  }

  @media (max-width: 600px) {
    .create-game-container {
      padding: 20px;
    }

    .settings-row {
      grid-template-columns: 1fr;
    }
  }
</style>
