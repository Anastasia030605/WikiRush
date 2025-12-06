<script>
  import { onMount, onDestroy } from 'svelte';
  import { push } from 'svelte-spa-router';
  import apiClient from '../lib/utils/axios';

  export let params = {};
  let gameId = params.id;

  let game = null;
  let loading = true;
  let error = '';
  let ws = null;

  let currentArticle = '';
  let targetArticle = '';
  let availableLinks = [];
  let searchQuery = '';
  let filteredLinks = [];

  let participant = null;
  let stepsCount = 0;
  let timeRemaining = 0;
  let timer = null;
  let isGameStarted = false;
  let isGameFinished = false;
  let isWinner = false;

  let notifications = [];

  $: filteredLinks = searchQuery
    ? availableLinks.filter(link =>
        link.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : availableLinks;

  async function loadGame() {
    try {
      const response = await apiClient.get(`/games/${gameId}`);
      game = response.data;
      targetArticle = game.target_article;

      const token = localStorage.getItem('access_token');
      if (token) {
        const userResponse = await apiClient.get('/users/me');
        const currentUserId = userResponse.data.id;
        participant = game.participants.find(p => p.user_id === currentUserId);

        if (participant) {
          currentArticle = participant.current_article || game.start_article;
          stepsCount = participant.steps_count;
          isGameFinished = participant.is_finished;
          isWinner = participant.is_winner;
        }
      }

      isGameStarted = game.status === 'in_progress';

      if (isGameStarted && !isGameFinished) {
        startTimer();
        loadAvailableLinks();
      }

      loading = false;
    } catch (err) {
      console.error('Error loading game:', err);
      error = err.response?.data?.detail || 'Failed to load game';
      loading = false;
    }
  }

  async function loadAvailableLinks() {
    try {
      const response = await apiClient.get(`/games/${gameId}/available-links`);
      availableLinks = response.data.available_links;
      currentArticle = response.data.current_article;
      targetArticle = response.data.target_article;
    } catch (err) {
      console.error('Error loading links:', err);
      addNotification('Error loading links', 'error');
    }
  }

  async function joinGame() {
    try {
      await apiClient.post(`/games/${gameId}/join`);
      await loadGame();
      addNotification('You joined the game!', 'success');
    } catch (err) {
      console.error('Error joining game:', err);
      error = err.response?.data?.detail || 'Failed to join game';
    }
  }

  async function startGame() {
    try {
      await apiClient.post(`/games/${gameId}/start`);
      await loadGame();
    } catch (err) {
      console.error('Error starting game:', err);
      error = err.response?.data?.detail || 'Failed to start game';
    }
  }

  async function makeMove(article) {
    try {
      const response = await apiClient.post(`/games/${gameId}/move`, {
        article
      });

      currentArticle = response.data.current_article;
      stepsCount = response.data.steps_count;

      if (response.data.is_target_reached) {
        isWinner = true;
        isGameFinished = true;
        stopTimer();
        addNotification('Congratulations! You won!', 'success');
      } else {
        searchQuery = '';
        await loadAvailableLinks();
      }
    } catch (err) {
      console.error('Error making move:', err);
      addNotification(err.response?.data?.detail || 'Move error', 'error');
    }
  }

  function connectWebSocket() {
    const wsUrl = `ws://localhost:8000/api/v1/games/${gameId}/ws`;
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setTimeout(() => {
        if (!isGameFinished) {
          connectWebSocket();
        }
      }, 3000);
    };
  }

  function handleWebSocketMessage(data) {
    switch (data.type) {
      case 'player_joined':
        addNotification(`${data.username} joined the game`, 'info');
        loadGame();
        break;

      case 'game_started':
        addNotification('Game started!', 'success');
        loadGame();
        break;

      case 'player_move':
        addNotification(
          `${data.username} moved to "${data.article}" (step ${data.steps})`,
          'info'
        );
        break;

      case 'player_won':
        addNotification(
          `${data.username} won in ${data.steps} steps and ${Math.floor(data.time / 60)} min ${data.time % 60} sec!`,
          'success'
        );
        loadGame();
        break;
    }
  }

  function startTimer() {
    if (!game) return;

    const startTime = new Date(game.started_at).getTime();
    const timeLimit = game.time_limit * 1000;

    timer = setInterval(() => {
      const now = Date.now();
      const elapsed = now - startTime;
      const remaining = Math.max(0, timeLimit - elapsed);

      timeRemaining = Math.floor(remaining / 1000);

      if (timeRemaining === 0) {
        stopTimer();
        isGameFinished = true;
        addNotification('Time is up!', 'error');
      }
    }, 1000);
  }

  function stopTimer() {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
  }

  function addNotification(message, type = 'info') {
    const notification = { id: Date.now(), message, type };
    notifications = [notification, ...notifications];

    setTimeout(() => {
      notifications = notifications.filter(n => n.id !== notification.id);
    }, 5000);
  }

  function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  onMount(() => {
    loadGame();
    connectWebSocket();
  });

  onDestroy(() => {
    stopTimer();
    if (ws) {
      ws.close();
    }
  });
</script>

<div class="game-room">
  <div class="notifications">
    {#each notifications as notification (notification.id)}
      <div class="notification notification-{notification.type}">
        {notification.message}
      </div>
    {/each}
  </div>

  {#if loading}
    <div class="loading">Loading game...</div>
  {:else if error}
    <div class="error-message">
      <span>!</span>
      {error}
    </div>
  {:else if game}
    <div class="game-container">
      <div class="game-header">
        <div class="game-title">
          <h1>{game.start_article} -&gt; {game.target_article}</h1>
          <div class="game-badges">
            <span class="badge">{game.mode}</span>
            <span class="badge">{game.status}</span>
          </div>
        </div>

        {#if isGameStarted && !isGameFinished}
          <div class="game-stats">
            <div class="stat">
              <span class="stat-label">Steps</span>
              <span class="stat-value">{stepsCount}/{game.max_steps}</span>
            </div>
            <div class="stat">
              <span class="stat-label">Time</span>
              <span class="stat-value">{formatTime(timeRemaining)}</span>
            </div>
          </div>
        {/if}
      </div>

      {#if !participant}
        <div class="join-section">
          <p>You are not participating in this game</p>
          <button class="btn btn-primary" on:click={joinGame}>
            Join Game
          </button>
        </div>
      {:else if game.status === 'waiting'}
        <div class="waiting-section">
          <h2>Waiting for game to start</h2>
          <p>Players: {game.participants.length}/{game.max_players}</p>

          <div class="participants-list">
            {#each game.participants as p}
              <div class="participant-item">
                {p.user.username}
              </div>
            {/each}
          </div>

          {#if game.creator.id === participant.user_id}
            <button class="btn btn-primary" on:click={startGame}>
              Start Game
            </button>
          {:else}
            <p class="info-text">Waiting for creator to start the game...</p>
          {/if}
        </div>
      {:else if isGameFinished}
        <div class="finished-section">
          {#if isWinner}
            <h2>Congratulations! You won!</h2>
            <p>Steps taken: {stepsCount}</p>
          {:else}
            <h2>Game finished</h2>
            <p>You took {stepsCount} steps</p>
          {/if}

          <button class="btn btn-primary" on:click={() => push('/games')}>
            Back to Games List
          </button>
        </div>
      {:else if isGameStarted}
        <div class="game-play">
          <div class="current-article">
            <h2>Current Article:</h2>
            <h3>{currentArticle}</h3>
            <p class="target-hint">Goal: {targetArticle}</p>
          </div>

          <div class="links-section">
            <div class="search-box">
              <input
                type="text"
                bind:value={searchQuery}
                placeholder="Search links..."
                class="search-input"
              />
            </div>

            <div class="links-list">
              {#if filteredLinks.length === 0}
                <p class="no-links">No links available</p>
              {:else}
                {#each filteredLinks as link}
                  <button
                    class="link-item"
                    on:click={() => makeMove(link)}
                  >
                    {link}
                  </button>
                {/each}
              {/if}
            </div>
          </div>
        </div>
      {/if}

      <div class="participants-sidebar">
        <h3>Participants</h3>
        {#each game.participants as p}
          <div class="participant-card" class:participant-finished={p.is_finished} class:participant-winner={p.is_winner}>
            <div class="participant-name">{p.user.username}</div>
            <div class="participant-stats">
              {#if p.is_finished}
                {#if p.is_winner}
                  <span class="winner-badge">Winner!</span>
                {:else}
                  <span class="finished-badge">Finished</span>
                {/if}
              {/if}
              <span class="steps-badge">{p.steps_count} steps</span>
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  .game-room {
    min-height: calc(100vh - 100px);
    padding: 20px;
  }

  .loading, .error-message {
    text-align: center;
    padding: 60px 20px;
    font-size: 1.2rem;
  }

  .error-message {
    background: var(--light-pink);
    border: 2px solid var(--error);
    color: var(--error);
    padding: 20px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
  }

  .notifications {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .notification {
    background: white;
    padding: 15px 20px;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    min-width: 250px;
    animation: slideIn 0.3s ease;
  }

  .notification-success {
    border-left: 4px solid var(--success);
  }

  .notification-error {
    border-left: 4px solid var(--error);
  }

  .notification-info {
    border-left: 4px solid var(--primary-blue);
  }

  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  .game-container {
    max-width: 1400px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 300px;
    gap: 20px;
  }

  .game-header {
    grid-column: 1 / -1;
    background: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  }

  .game-title h1 {
    font-size: 1.8rem;
    color: var(--text-dark);
    margin-bottom: 10px;
  }

  .game-badges {
    display: flex;
    gap: 10px;
  }

  .badge {
    display: inline-block;
    padding: 6px 12px;
    background: var(--light-pink);
    color: var(--primary-pink);
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
  }

  .game-stats {
    display: flex;
    gap: 30px;
    margin-top: 20px;
  }

  .stat {
    display: flex;
    flex-direction: column;
  }

  .stat-label {
    font-size: 0.9rem;
    color: var(--text-light);
    margin-bottom: 5px;
  }

  .stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary-pink);
  }

  .join-section, .waiting-section, .finished-section {
    grid-column: 1 / -1;
    background: white;
    padding: 60px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    text-align: center;
  }

  .participants-list {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: center;
    margin: 20px 0;
  }

  .participant-item {
    background: var(--light-pink);
    padding: 10px 20px;
    border-radius: 20px;
    font-weight: 600;
  }

  .info-text {
    color: var(--text-light);
    margin: 20px 0;
  }

  .game-play {
    background: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  }

  .current-article {
    margin-bottom: 30px;
  }

  .current-article h2 {
    font-size: 1.2rem;
    color: var(--text-light);
    margin-bottom: 10px;
  }

  .current-article h3 {
    font-size: 2rem;
    color: var(--text-dark);
    margin-bottom: 10px;
  }

  .target-hint {
    color: var(--text-light);
    font-style: italic;
  }

  .links-section {
    margin-top: 30px;
  }

  .search-input {
    width: 100%;
    padding: 15px;
    border: 2px solid var(--secondary-pink);
    border-radius: 10px;
    font-size: 1rem;
    margin-bottom: 20px;
  }

  .search-input:focus {
    outline: none;
    border-color: var(--primary-pink);
    box-shadow: 0 0 0 3px rgba(255, 105, 180, 0.1);
  }

  .links-list {
    max-height: 500px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .link-item {
    background: var(--light-pink);
    border: 2px solid transparent;
    padding: 15px 20px;
    border-radius: 10px;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 1rem;
  }

  .link-item:hover {
    background: white;
    border-color: var(--primary-pink);
    transform: translateX(5px);
  }

  .no-links {
    text-align: center;
    color: var(--text-light);
    padding: 40px;
  }

  .participants-sidebar {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    height: fit-content;
  }

  .participants-sidebar h3 {
    font-size: 1.2rem;
    margin-bottom: 15px;
    color: var(--text-dark);
  }

  .participant-card {
    padding: 15px;
    border-radius: 10px;
    background: var(--light-pink);
    margin-bottom: 10px;
  }

  .participant-finished {
    background: #f0f9ff;
  }

  .participant-winner {
    background: #fef3c7;
    border: 2px solid #f59e0b;
  }

  .participant-name {
    font-weight: 600;
    margin-bottom: 8px;
  }

  .participant-stats {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }

  .winner-badge {
    color: #f59e0b;
    font-weight: 700;
  }

  .finished-badge {
    color: var(--primary-blue);
  }

  .steps-badge {
    font-size: 0.9rem;
    color: var(--text-light);
  }

  @media (max-width: 1024px) {
    .game-container {
      grid-template-columns: 1fr;
    }

    .participants-sidebar {
      order: -1;
    }
  }
</style>
