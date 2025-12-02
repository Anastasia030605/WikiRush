<script>
  export let game;
  
  function getStatusText(status) {
    const statusMap = {
      'waiting': 'Ожидание игроков',
      'in_progress': 'В процессе',
      'finished': 'Завершена'
    };
    return statusMap[status] || status;
  }

  function getStatusClass(status) {
    const classMap = {
      'waiting': 'status-waiting',
      'in_progress': 'status-progress',
      'finished': 'status-finished'
    };
    return classMap[status] || '';
  }
</script>

<div class="game-card card">
  <div class="game-header">
    <h3>Игра #{game.id}</h3>
    <span class="status {getStatusClass(game.status)}">
      {getStatusText(game.status)}
    </span>
  </div>

  <div class="game-info">
    <div class="info-row">
      <span class="label">📖 От:</span>
      <span class="value">{game.start_article}</span>
    </div>
    <div class="info-row">
      <span class="label">🎯 До:</span>
      <span class="value">{game.target_article}</span>
    </div>
    <div class="info-row">
      <span class="label">👥 Игроки:</span>
      <span class="value">{game.current_players || 0} / {game.max_players || '∞'}</span>
    </div>
  </div>

  <div class="game-footer">
    <a href="#/games/{game.id}" class="btn btn-primary btn-sm">
      {game.status === 'waiting' ? 'Присоединиться' : 'Смотреть'}
    </a>
  </div>
</div>

<style>
  .game-card {
    transition: all 0.3s ease;
  }

  .game-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px var(--shadow);
  }

  .game-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 2px solid var(--light-pink);
  }

  .game-header h3 {
    margin: 0;
    color: var(--text-dark);
    font-size: 1.3rem;
  }

  .status {
    padding: 6px 12px;
    border-radius: 15px;
    font-size: 0.85rem;
    font-weight: 600;
  }

  .status-waiting {
    background: var(--light-green);
    color: var(--primary-green);
  }

  .status-progress {
    background: var(--light-pink);
    color: var(--primary-pink);
  }

  .status-finished {
    background: #f0f0f0;
    color: #888;
  }

  .game-info {
    margin-bottom: 16px;
  }

  .info-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
    align-items: center;
  }

  .label {
    color: var(--text-light);
    font-weight: 500;
  }

  .value {
    color: var(--text-dark);
    font-weight: 600;
    text-align: right;
    max-width: 60%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .game-footer {
    display: flex;
    justify-content: flex-end;
  }

  .btn-sm {
    padding: 8px 20px;
    font-size: 0.9rem;
  }
</style>