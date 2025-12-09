<script>
  import { onMount } from 'svelte';
  import { push } from 'svelte-spa-router';
  import apiClient from '../lib/utils/axios';
  import { user } from '../lib/stores/auth';

  let currentUser = null;
  let games = [];
  let loading = true;
  let error = '';
  let activeTab = 'active'; // 'active' or 'archive'
  let statusFilter = '';
  let modeFilter = '';
  let page = 1;
  let pageSize = 20;
  let total = 0;

  // Subscribe to user store
  user.subscribe(value => {
    currentUser = value;
  });

  const statusLabels = {
    waiting: 'Waiting',
    in_progress: 'In Progress',
    finished: 'Finished',
    cancelled: 'Cancelled'
  };

  const modeLabels = {
    single: 'Single',
    multiplayer: 'Multiplayer',
    race: 'Race'
  };

  async function loadGames() {
    loading = true;
    error = '';

    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString()
      });

      // Apply status filter based on active tab
      if (activeTab === 'active') {
        // Show only waiting and in_progress games
        if (statusFilter) {
          params.append('status', statusFilter);
        }
      } else {
        // Archive tab: we'll filter on client side to include both finished and cancelled
      }

      if (modeFilter) params.append('mode', modeFilter);

      const response = await apiClient.get(`/games?${params.toString()}`);

      // Filter games based on active tab
      if (activeTab === 'active') {
        // Active tab: show only waiting and in_progress games
        if (!statusFilter) {
          games = response.data.games.filter(game =>
            game.status === 'waiting' || game.status === 'in_progress'
          );
        } else {
          games = response.data.games;
        }
      } else {
        // Archive tab: show only finished and cancelled games
        games = response.data.games.filter(game =>
          game.status === 'finished' || game.status === 'cancelled'
        );
      }

      total = response.data.total;
    } catch (err) {
      console.error('Error loading games:', err);
      error = err.response?.data?.detail || 'Failed to load games list';
    } finally {
      loading = false;
    }
  }

  function handleFilterChange() {
    page = 1;
    loadGames();
  }

  function switchTab(tab) {
    activeTab = tab;
    statusFilter = ''; // Reset status filter when switching tabs
    page = 1;
    loadGames();
  }

  function nextPage() {
    if (page * pageSize < total) {
      page++;
      loadGames();
    }
  }

  function prevPage() {
    if (page > 1) {
      page--;
      loadGames();
    }
  }

  function isUserParticipant(game) {
    if (!currentUser) return false;
    // For single player games, creator is always the only participant
    if (game.mode === 'single') {
      return game.creator.id === currentUser.id;
    }
    // For multiplayer games, we would need the participants array
    // For now, assume not a participant if not the creator
    return game.creator.id === currentUser.id;
  }

  async function joinGame(gameId, game) {
    const isParticipant = isUserParticipant(game);

    // Join game if not already a participant
    if (game.status === 'waiting' && !isParticipant) {
      try {
        await apiClient.post(`/games/${gameId}/join`);
      } catch (err) {
        console.error('Error joining game:', err);
      }
    }

    // Navigate to game page (without auto-starting)
    push(`/game/${gameId}`);
  }

  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  onMount(() => {
    loadGames();
  });
</script>

<div class="games-list-page">
  <div class="container">
    <div class="header">
      <h1>Games</h1>
      <button class="btn btn-primary" on:click={() => push('/create-game')}>
        Create Game
      </button>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button
        class="tab"
        class:active={activeTab === 'active'}
        on:click={() => switchTab('active')}
      >
        Active Games
      </button>
      <button
        class="tab"
        class:active={activeTab === 'archive'}
        on:click={() => switchTab('archive')}
      >
        Archive
      </button>
    </div>

    <div class="filters">
      {#if activeTab === 'active'}
        <div class="filter-group">
          <label for="status">Status</label>
          <select id="status" bind:value={statusFilter} on:change={handleFilterChange}>
            <option value="">All</option>
            <option value="waiting">Waiting</option>
            <option value="in_progress">In Progress</option>
          </select>
        </div>
      {/if}

      <div class="filter-group">
        <label for="mode">Mode</label>
        <select id="mode" bind:value={modeFilter} on:change={handleFilterChange}>
          <option value="">All</option>
          <option value="single">Single</option>
          <option value="multiplayer">Multiplayer</option>
          <option value="race">Race</option>
        </select>
      </div>
    </div>

    {#if error}
      <div class="error-message">
        <span>!</span>
        {error}
      </div>
    {/if}

    {#if loading}
      <div class="loading">Loading...</div>
    {:else if games.length === 0}
      <div class="empty-state">
        <p>No games available</p>
        <button class="btn btn-primary" on:click={() => push('/create-game')}>
          Create First Game
        </button>
      </div>
    {:else}
      <div class="games-grid">
        {#each games as game}
          <div class="game-card card">
            <div class="game-header">
              <h3>{game.start_article} -&gt; {game.target_article}</h3>
              <span class="status-badge status-{game.status}">
                {statusLabels[game.status] || game.status}
              </span>
            </div>

            <div class="game-info">
              <div class="info-item">
                <span class="label">Mode:</span>
                <span class="value">{modeLabels[game.mode] || game.mode}</span>
              </div>
              <div class="info-item">
                <span class="label">Creator:</span>
                <span class="value">{game.creator.username}</span>
              </div>
              <div class="info-item">
                <span class="label">Players:</span>
                <span class="value">{game.participants_count}/{game.max_players}</span>
              </div>
              <div class="info-item">
                <span class="label">Max Steps:</span>
                <span class="value">{game.max_steps}</span>
              </div>
              <div class="info-item">
                <span class="label">Time:</span>
                <span class="value">{Math.floor(game.time_limit / 60)} min</span>
              </div>
              <div class="info-item">
                <span class="label">Created:</span>
                <span class="value">{formatDate(game.created_at)}</span>
              </div>
            </div>

            <button
              class="btn btn-primary btn-block"
              on:click={() => joinGame(game.id, game)}
              disabled={game.status === 'finished' || (game.status === 'waiting' && !isUserParticipant(game) && game.participants_count >= game.max_players)}
            >
              {#if game.status === 'finished'}
                Game Finished
              {:else if game.status === 'waiting' && !isUserParticipant(game) && game.participants_count >= game.max_players}
                Game Full
              {:else if game.status === 'waiting' && isUserParticipant(game)}
                Enter Game
              {:else if game.status === 'waiting'}
                Join
              {:else}
                Watch
              {/if}
            </button>
          </div>
        {/each}
      </div>

      <div class="pagination">
        <button class="btn btn-secondary" on:click={prevPage} disabled={page === 1}>
          Previous
        </button>
        <span class="page-info">
          Page {page} of {Math.ceil(total / pageSize)}
        </span>
        <button class="btn btn-secondary" on:click={nextPage} disabled={page * pageSize >= total}>
          Next
        </button>
      </div>
    {/if}
  </div>
</div>

<style>
  .games-list-page {
    padding: 40px 20px;
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
  }

  .header h1 {
    font-size: 2.5rem;
    color: var(--text-dark);
  }

  .tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    border-bottom: 2px solid var(--light-pink);
  }

  .tab {
    padding: 12px 24px;
    background: none;
    border: none;
    border-bottom: 3px solid transparent;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-light);
    transition: all 0.3s ease;
    margin-bottom: -2px;
  }

  .tab:hover {
    color: var(--primary-pink);
  }

  .tab.active {
    color: var(--primary-pink);
    border-bottom-color: var(--primary-pink);
  }

  .filters {
    display: flex;
    gap: 20px;
    margin-bottom: 30px;
    padding: 20px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  }

  .filter-group {
    flex: 1;
  }

  .filter-group label {
    display: block;
    margin-bottom: 8px;
    color: var(--text-dark);
    font-weight: 500;
  }

  select {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid var(--secondary-pink);
    border-radius: 10px;
    font-size: 1rem;
    transition: all 0.3s ease;
  }

  select:focus {
    outline: none;
    border-color: var(--primary-pink);
    box-shadow: 0 0 0 3px rgba(255, 105, 180, 0.1);
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

  .loading {
    text-align: center;
    padding: 60px 20px;
    font-size: 1.2rem;
    color: var(--text-light);
  }

  .empty-state {
    text-align: center;
    padding: 60px 20px;
  }

  .empty-state p {
    font-size: 1.2rem;
    color: var(--text-light);
    margin-bottom: 20px;
  }

  .games-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
  }

  .game-card {
    padding: 20px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }

  .game-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  }

  .game-header {
    margin-bottom: 15px;
  }

  .game-header h3 {
    font-size: 1.1rem;
    color: var(--text-dark);
    margin-bottom: 8px;
    word-break: break-word;
  }

  .status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
  }

  .status-waiting {
    background: var(--light-blue);
    color: var(--primary-blue);
  }

  .status-in_progress {
    background: var(--light-yellow);
    color: #d97706;
  }

  .status-finished {
    background: var(--light-pink);
    color: var(--primary-pink);
  }

  .status-cancelled {
    background: #fee;
    color: #dc2626;
  }

  .game-info {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 20px;
  }

  .info-item {
    display: flex;
    flex-direction: column;
  }

  .info-item .label {
    font-size: 0.85rem;
    color: var(--text-light);
    margin-bottom: 4px;
  }

  .info-item .value {
    font-weight: 600;
    color: var(--text-dark);
  }

  .btn-block {
    width: 100%;
  }

  .pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
  }

  .page-info {
    color: var(--text-dark);
    font-weight: 500;
  }

  @media (max-width: 768px) {
    .header {
      flex-direction: column;
      gap: 15px;
      align-items: flex-start;
    }

    .filters {
      flex-direction: column;
    }

    .games-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
