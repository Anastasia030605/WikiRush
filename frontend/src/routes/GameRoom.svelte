<script>
  import { onMount, onDestroy, tick } from 'svelte';
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
  let targetDescription = '';
  let availableLinks = [];
  let searchQuery = '';
  let filteredLinks = [];
  let articleHtml = '';
  let articleLoading = false;

  let participant = null;
  let stepsCount = 0;
  let timeRemaining = 0;
  let timer = null;
  let isGameStarted = false;
  let isGameFinished = false;
  let isWinner = false;

  let notifications = [];

  // Tooltip state
  let tooltipVisible = false;
  let tooltipContent = '';
  let tooltipTitle = '';
  let tooltipX = 0;
  let tooltipY = 0;
  let tooltipLoading = false;
  let currentHoverTimeout = null;

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

      // Load target description early
      if (targetArticle && !targetDescription) {
        try {
          const targetInfo = await apiClient.get(`/wikipedia/article/${encodeURIComponent(targetArticle)}/summary`);
          const fullText = targetInfo.data.extract || '';
          targetDescription = truncateText(fullText, 3);
        } catch (err) {
          console.error('Error loading target description:', err);
        }
      }

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

      // Auto-start single player game if participant joined but game not started
      if (game.mode === 'single' && game.status === 'waiting' && participant) {
        try {
          await apiClient.post(`/games/${gameId}/start`);
          await loadGame(); // Reload to get updated status
          return;
        } catch (err) {
          console.error('Error auto-starting game:', err);
        }
      }

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

      // Only update targetDescription if we have a new one (don't overwrite with empty)
      if (response.data.target_description) {
        targetDescription = truncateText(response.data.target_description, 3);
      }

      console.log('=== AVAILABLE LINKS LOADED ===');
      console.log('Current article:', currentArticle);
      console.log('Total available links:', availableLinks.length);
      console.log('First 20 available links:', availableLinks.slice(0, 20));
      console.log('Sample link charCodes:', availableLinks[0] ? Array.from(availableLinks[0]).map(c => c.charCodeAt(0)) : 'No links');

      // Load article content
      await loadArticleContent(currentArticle);
    } catch (err) {
      console.error('Error loading links:', err);
      addNotification('Error loading links', 'error');
    }
  }

  async function loadArticleContent(title) {
    try {
      articleLoading = true;
      const response = await apiClient.get(`/wikipedia/article/${encodeURIComponent(title)}/content`);
      articleHtml = response.data.html;

      // After DOM updates, attach click handlers to links
      // Wait for Svelte to update the DOM
      await tick();
      // Add additional delay to ensure DOM is ready
      await new Promise(resolve => setTimeout(resolve, 100));

      console.log('About to attach link handlers...');
      attachLinkHandlers();
    } catch (err) {
      console.error('Error loading article content:', err);
      addNotification('Error loading article content', 'error');
    } finally {
      articleLoading = false;
    }
  }

  // Svelte action to handle article links
  function setupArticleLinks(node) {
    console.log('setupArticleLinks action called on node:', node);

    function processLinks() {
      const links = node.querySelectorAll('a');
      console.log(`Found ${links.length} links in article`);

      links.forEach(link => {
        const href = link.getAttribute('href');

        // Only modify Wikipedia links
        if (href && (href.startsWith('/wiki/') || href.includes('wikipedia.org/wiki/'))) {
          console.log('Processing wiki link:', href);

          // Extract article title for tooltip
          let articleTitle = '';
          if (href.startsWith('/wiki/')) {
            articleTitle = href.substring(6);
          } else if (href.includes('wikipedia.org/wiki/')) {
            const match = href.match(/wikipedia\.org\/wiki\/(.+)/);
            if (match) {
              articleTitle = match[1];
            }
          }

          // Clean up the title
          if (articleTitle.includes('#')) {
            articleTitle = articleTitle.split('#')[0];
          }
          if (articleTitle.includes('?')) {
            articleTitle = articleTitle.split('?')[0];
          }
          articleTitle = decodeURIComponent(articleTitle);
          articleTitle = articleTitle.replace(/_/g, ' ');

          // Create a span element to replace the link
          const span = document.createElement('span');
          span.className = 'wiki-link';
          span.setAttribute('data-wiki-href', href);
          span.setAttribute('data-article-title', articleTitle);
          span.innerHTML = link.innerHTML;
          span.style.cssText = link.style.cssText;

          // Copy all classes from the original link
          link.classList.forEach(cls => {
            if (cls !== 'wiki-link') {
              span.classList.add(cls);
            }
          });

          // Add click handler
          span.addEventListener('click', handleArticleLinkClick);

          // Add hover handlers for tooltip
          span.addEventListener('mouseenter', (e) => {
            showTooltip(e, articleTitle);
          });
          span.addEventListener('mouseleave', hideTooltip);

          // Replace the link with the span
          link.parentNode.replaceChild(span, link);
        }
      });

      console.log('Link handlers attached via action');
    }

    // Process links immediately
    processLinks();

    return {
      update() {
        console.log('setupArticleLinks update called');
        processLinks();
      },
      destroy() {
        // Cleanup if needed
      }
    };
  }

  function attachLinkHandlers() {
    const articleContainer = document.querySelector('.article-content');
    if (!articleContainer) {
      console.log('Article container not found');
      return;
    }

    const links = articleContainer.querySelectorAll('a');
    console.log(`Found ${links.length} links in article`);

    links.forEach(link => {
      const href = link.getAttribute('href');

      // Only modify Wikipedia links
      if (href && (href.startsWith('/wiki/') || href.includes('wikipedia.org/wiki/'))) {
        console.log('Processing wiki link:', href);

        // Create a span element to replace the link
        const span = document.createElement('span');
        span.className = 'wiki-link';
        span.setAttribute('data-wiki-href', href);
        span.innerHTML = link.innerHTML;
        span.style.cssText = link.style.cssText;

        // Copy all classes from the original link
        link.classList.forEach(cls => {
          if (cls !== 'wiki-link') {
            span.classList.add(cls);
          }
        });

        // Add click handler
        span.addEventListener('click', handleArticleLinkClick);

        // Replace the link with the span
        link.parentNode.replaceChild(span, link);
      }
    });

    console.log('Link handlers attached');
  }

  function truncateText(text, maxSentences = 2, maxChars = 300) {
    if (!text) return text;

    // First, limit by character count if text is too long
    let result = text;
    if (text.length > maxChars) {
      // Find last complete sentence within maxChars
      result = text.substring(0, maxChars);
      const lastPeriod = Math.max(
        result.lastIndexOf('.'),
        result.lastIndexOf('!'),
        result.lastIndexOf('?')
      );

      if (lastPeriod > maxChars * 0.5) {
        // If we found a sentence ending in the second half, use it
        result = text.substring(0, lastPeriod + 1);
      } else {
        // Otherwise just cut and add ellipsis
        result = result.trim() + '...';
        return result;
      }
    }

    // Then, limit by sentence count
    const sentences = result.match(/[^.!?]+[.!?]+/g) || [result];
    const truncated = sentences.slice(0, maxSentences).join(' ');

    // If we truncated, add ellipsis
    if (sentences.length > maxSentences || text.length > result.length) {
      return truncated + '...';
    }

    return truncated;
  }

  async function showTooltip(event, articleTitle) {
    // Clear any existing timeout
    if (currentHoverTimeout) {
      clearTimeout(currentHoverTimeout);
    }

    // Set loading state and position immediately
    const rect = event.currentTarget.getBoundingClientRect();
    tooltipX = rect.left + (rect.width / 2);
    tooltipY = rect.bottom + 10;
    tooltipVisible = true;
    tooltipLoading = true;
    tooltipTitle = articleTitle;
    tooltipContent = '';

    // Delay fetching to avoid too many requests on quick hovers
    currentHoverTimeout = setTimeout(async () => {
      try {
        const response = await apiClient.get(`/wikipedia/article/${encodeURIComponent(articleTitle)}/summary`);
        if (tooltipVisible && tooltipTitle === articleTitle) {
          const fullText = response.data.extract || 'No description available';
          tooltipContent = truncateText(fullText, 2);
          tooltipLoading = false;
        }
      } catch (err) {
        console.error('Error loading tooltip:', err);
        if (tooltipVisible && tooltipTitle === articleTitle) {
          tooltipContent = 'Failed to load preview';
          tooltipLoading = false;
        }
      }
    }, 500); // 500ms delay before fetching
  }

  function hideTooltip() {
    if (currentHoverTimeout) {
      clearTimeout(currentHoverTimeout);
      currentHoverTimeout = null;
    }
    tooltipVisible = false;
    tooltipLoading = false;
    tooltipContent = '';
    tooltipTitle = '';
  }

  function handleArticleLinkClick(event) {
    console.log('=== WIKI LINK CLICKED ===');
    console.log('Event:', event);

    // Hide tooltip on click
    hideTooltip();

    event.preventDefault();
    event.stopPropagation();

    const target = event.currentTarget;
    console.log('Target element:', target);

    const href = target.getAttribute('data-wiki-href');

    if (!href) {
      console.log('ERROR: No data-wiki-href found on element');
      console.log('Element attributes:', target.attributes);
      return;
    }

    console.log('Link clicked:', href);

    // Extract article title from Wikipedia link
    let articleTitle = '';

    if (href.startsWith('/wiki/')) {
      // Remove /wiki/ prefix
      articleTitle = href.substring(6);
    } else if (href.includes('wikipedia.org/wiki/')) {
      const match = href.match(/wikipedia\.org\/wiki\/(.+)/);
      if (match) {
        articleTitle = match[1];
      }
    }

    // Remove hash/anchor if present (e.g., #History)
    if (articleTitle.includes('#')) {
      articleTitle = articleTitle.split('#')[0];
    }

    // Remove query parameters if present (e.g., ?action=edit)
    if (articleTitle.includes('?')) {
      articleTitle = articleTitle.split('?')[0];
    }

    // Decode URL encoding
    articleTitle = decodeURIComponent(articleTitle);

    // Replace underscores with spaces (Wikipedia uses underscores in URLs but spaces in titles)
    articleTitle = articleTitle.replace(/_/g, ' ');

    console.log('Extracted article title:', articleTitle);
    console.log('Available links count:', availableLinks.length);
    console.log('Available links (first 10):', availableLinks.slice(0, 10));

    // Find similar links for debugging
    const similarLinks = availableLinks.filter(link =>
      link.toLowerCase().includes(articleTitle.toLowerCase().substring(0, 10)) ||
      articleTitle.toLowerCase().includes(link.toLowerCase().substring(0, 10))
    );
    console.log('Similar links:', similarLinks);
    console.log('Is available (exact match):', availableLinks.includes(articleTitle));

    if (!articleTitle) {
      console.log('Could not extract article title');
      return;
    }

    if (availableLinks.includes(articleTitle)) {
      console.log('Making move to:', articleTitle);
      makeMove(articleTitle);
    } else {
      console.log('Link not available - trying to find exact match');
      console.log('Article title length:', articleTitle.length);
      console.log('Article title charCodes:', Array.from(articleTitle).map(c => c.charCodeAt(0)));
      addNotification(`"${articleTitle}" is not available from current article`, 'error');
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
        // Load new article content and available links
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

    // Parse started_at - add 'Z' if no timezone specified to treat as UTC
    let startedAtString = game.started_at;
    if (!startedAtString.endsWith('Z') && !startedAtString.includes('+')) {
      startedAtString += 'Z';
    }
    const startTime = new Date(startedAtString).getTime();
    const timeLimit = game.time_limit * 1000;

    timer = setInterval(() => {
      const now = Date.now();
      const elapsed = now - startTime;
      const remaining = Math.max(0, timeLimit - elapsed);

      timeRemaining = Math.floor(remaining / 1000);

      if (timeRemaining === 0 && !isGameFinished) {
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

  <!-- Article preview tooltip -->
  {#if tooltipVisible}
    <div class="article-tooltip" style="left: {tooltipX}px; top: {tooltipY}px;">
      <div class="tooltip-title">{tooltipTitle}</div>
      {#if tooltipLoading}
        <div class="tooltip-loading">Loading...</div>
      {:else}
        <div class="tooltip-content">{tooltipContent}</div>
      {/if}
    </div>
  {/if}

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
          {#if targetDescription}
            <p class="target-description-header">{targetDescription}</p>
          {/if}
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
          <div class="current-article-header">
            <h2>{currentArticle}</h2>
            <p class="target-hint">Goal: <strong>{targetArticle}</strong></p>
            {#if targetDescription}
              <p class="target-description">{targetDescription}</p>
            {/if}
          </div>

          {#if articleLoading}
            <div class="article-loading">Loading article...</div>
          {:else if articleHtml}
            <div class="article-content" use:setupArticleLinks>
              {@html articleHtml}
            </div>
          {:else}
            <div class="article-error">Failed to load article content</div>
          {/if}
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

  .target-description-header {
    color: var(--text-light);
    font-size: 0.95rem;
    line-height: 1.5;
    margin: 15px 0;
    padding: 12px;
    background: var(--light-pink);
    border-radius: 8px;
    border-left: 4px solid var(--primary-pink);
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
    max-height: calc(100vh - 200px);
    overflow-y: auto;
  }

  .current-article-header {
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 2px solid var(--light-pink);
    position: sticky;
    top: 0;
    background: white;
    z-index: 10;
  }

  .current-article-header h2 {
    font-size: 1.8rem;
    color: var(--text-dark);
    margin-bottom: 10px;
  }

  .target-hint {
    color: var(--text-light);
    font-size: 1rem;
    margin-bottom: 8px;
  }

  .target-hint strong {
    color: var(--primary-pink);
    font-weight: 700;
  }

  .target-description {
    color: var(--text-light);
    font-size: 0.95rem;
    line-height: 1.5;
    margin-top: 10px;
    padding: 12px;
    background: var(--light-pink);
    border-radius: 8px;
    border-left: 4px solid var(--primary-pink);
  }

  .article-loading, .article-error {
    text-align: center;
    padding: 60px 20px;
    font-size: 1.1rem;
    color: var(--text-light);
  }

  .article-error {
    color: var(--error);
  }

  :global(.article-content) {
    font-size: 1rem;
    line-height: 1.7;
    color: var(--text-dark);
  }

  :global(.article-content p) {
    margin-bottom: 1rem;
  }

  :global(.article-content a),
  :global(.article-content .wiki-link) {
    color: var(--primary-blue) !important;
    text-decoration: underline !important;
    border-bottom: 1px solid transparent;
    transition: all 0.2s ease;
    cursor: pointer !important;
    font-weight: 500;
  }

  :global(.article-content a:hover),
  :global(.article-content .wiki-link:hover) {
    color: var(--primary-pink) !important;
    border-bottom-color: var(--primary-pink);
    text-decoration: none !important;
    background-color: rgba(236, 72, 153, 0.1);
    padding: 2px 4px;
    border-radius: 3px;
  }

  :global(.article-content a:visited),
  :global(.article-content .wiki-link:visited) {
    color: #7c3aed !important;
  }

  :global(.article-content h1),
  :global(.article-content h2),
  :global(.article-content h3) {
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
    color: var(--text-dark);
  }

  :global(.article-content img) {
    max-width: 100%;
    height: auto;
    border-radius: 5px;
  }

  :global(.article-content table) {
    border-collapse: collapse;
    margin: 1rem 0;
    width: 100%;
  }

  :global(.article-content th),
  :global(.article-content td) {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
  }

  :global(.article-content th) {
    background-color: var(--light-pink);
  }

  :global(.article-content ul),
  :global(.article-content ol) {
    margin-left: 2rem;
    margin-bottom: 1rem;
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

  .article-tooltip {
    position: fixed;
    transform: translateX(-50%);
    background: white;
    border: 2px solid var(--primary-pink);
    border-radius: 10px;
    padding: 15px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    max-width: 400px;
    min-width: 250px;
    z-index: 9999;
    animation: tooltipFadeIn 0.2s ease;
    pointer-events: none;
  }

  @keyframes tooltipFadeIn {
    from {
      opacity: 0;
      transform: translateX(-50%) translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }
  }

  .tooltip-title {
    font-weight: 700;
    font-size: 1rem;
    color: var(--primary-pink);
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--light-pink);
  }

  .tooltip-loading {
    color: var(--text-light);
    font-size: 0.9rem;
    font-style: italic;
    padding: 10px 0;
  }

  .tooltip-content {
    color: var(--text-dark);
    font-size: 0.9rem;
    line-height: 1.5;
  }

  @media (max-width: 1024px) {
    .game-container {
      grid-template-columns: 1fr;
    }

    .participants-sidebar {
      order: -1;
    }

    .article-tooltip {
      max-width: 90vw;
      left: 50% !important;
    }
  }
</style>
