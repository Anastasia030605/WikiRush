<script>
  export let players = [];
  export let currentUserId = null;
</script>

<div class="player-list card">
  <h3>👥 Игроки ({players.length})</h3>
  <div class="players">
    {#each players as player}
      <div class="player" class:current={player.user_id === currentUserId}>
        <div class="player-info">
          <span class="player-name">
            {player.username || `Игрок ${player.user_id}`}
            {#if player.user_id === currentUserId}
              <span class="you-badge">ты</span>
            {/if}
          </span>
          <span class="player-status">
            {player.status === 'ready' ? '✅ Готов' : '⏳ Ожидание'}
          </span>
        </div>
        {#if player.current_article}
          <div class="player-progress">
            📍 {player.current_article}
            <span class="steps">({player.moves || 0} шагов)</span>
          </div>
        {/if}
      </div>
    {/each}
  </div>
</div>

<style>
  .player-list {
    margin-bottom: 20px;
  }

  .player-list h3 {
    margin-bottom: 16px;
    color: var(--text-dark);
  }

  .players {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .player {
    padding: 12px;
    background: var(--light-green);
    border-radius: 12px;
    transition: all 0.3s ease;
  }

  .player.current {
    background: linear-gradient(135deg, var(--light-pink), var(--light-green));
    border: 2px solid var(--primary-pink);
  }

  .player-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
  }

  .player-name {
    font-weight: 600;
    color: var(--text-dark);
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .you-badge {
    background: var(--primary-pink);
    color: white;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 0.75rem;
    font-weight: 700;
  }

  .player-status {
    font-size: 0.9rem;
    color: var(--text-light);
  }

  .player-progress {
    font-size: 0.85rem;
    color: var(--text-light);
    margin-top: 4px;
  }

  .steps {
    color: var(--primary-green);
    font-weight: 600;
  }
</style>