<script>
  import { onMount } from 'svelte';
  import { push } from 'svelte-spa-router';
  import { gamesAPI } from '../lib/api/games';
  import { isAuthenticated } from '../lib/stores/auth';
  import GameCard from '../lib/components/GameCard.svelte';

  let games = [];
  let loading = true;
  let error = '';

  onMount(async () => {
    if (!$isAuthenticated) {
      push('/login');
      return;
    }

    await loadGames();
  });

  async function loadGames() {
    try {
      loading = true;
      games = await gamesAPI.getGames();
    } catch (err) {
      console.error('Ошибка загрузки игр:', err);
      error = 'Не удалось загрузить список игр';
    } finally {
      loading = false;
    }
  }
</script>

<div class="games-list-page">
  <div class="page-header">
    <div>
      <h1>🎮 Все игры</h1>
      <p>Присоединяйся к игре или создай свою!</p>
    </div>
    <a href="#/games/create" class="btn btn-primary">
      ➕ Создать игру
    </a>
  </div>

  {#if loading}
    <div class="loading">
      <div class="spinner"></div>
      <p>Загрузка игр...</p>
    </div>
  {:else if error}
    <div class="error-message">
      <span>⚠️</span>
      {error}
    </div>
  {:else if games.length === 0}
    <div class="empty-state card">
      <span class="emoji">🎯</span>
      <h2>Пока нет активных игр</h2>
      <p>Будь первым! Создай новую игру прямо сейчас</p>
      <a href="#/games/create" class="btn btn-primary btn-lg">
        Создать первую игру
      </a>
    </div>
  {:else}
    <div class="games-grid">
      {#each games as game}
        <GameCard {game} />
      {/each}
    </div>
  {/if}

  <button on:click={loadGames} class="btn btn-secondary refresh-btn">
    🔄 Обновить список
  </button>
</div>

<style>
  .games-list-page {
    max-width: 1200px;
    margin: 0 auto;
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 40px;
  }

  .page-header h1 {
    font-size: 2.5rem;
    margin-bottom: 8px;
    color: var(--text-dark);
  }

  .page-header p {
    color: var(--text-light);
    font-size: 1.1rem;
  }

  .loading {
    text-align: center;
    padding: 60px 20px;
  }

  .spinner {
    width: 50px;
    height: 50px;
    border: 4px solid var(--secondary-pink);
    border-top-color: var(--primary-pink);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 20px;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .error-message {
    background: var(--light-pink);
    border: 2px solid var(--error);
    color: var(--error);
    padding: 16px 20px;
    border-radius: 15px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 1.1rem;
  }

  .empty-state {
    text-align: center;
    padding: 60px 40px;
    max-width: 500px;
    margin: 0 auto;
  }

  .empty-state .emoji {
    font-size: 4rem;
    display: block;
    margin-bottom: 20px;
  }

  .empty-state h2 {
    font-size: 1.8rem;
    margin-bottom: 12px;
    color: var(--text-dark);
  }

  .empty-state p {
    color: var(--text-light);
    margin-bottom: 24px;
    font-size: 1.1rem;
  }

  .btn-lg {
    padding: 16px 32px;
    font-size: 1.1rem;
  }

  .games-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 24px;
    margin-bottom: 30px;
  }

  .refresh-btn {
    display: block;
    margin: 0 auto;
  }
</style>