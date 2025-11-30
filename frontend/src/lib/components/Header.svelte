<script>
  import { isAuthenticated, user, clearUser } from '../stores/auth';
  import { push } from 'svelte-spa-router';

  function handleLogout() {
    clearUser();
    push('/login');
  }
</script>

<header>
  <div class="container">
    <a href="#/" class="logo">
      <span class="emoji">🏁</span>
      <span class="title">WikiRush</span>
    </a>
    
    <nav>
      {#if $isAuthenticated}
        <a href="#/games" class="nav-link">Игры</a>
        <a href="#/leaderboard" class="nav-link">Лидеры</a>
        <a href="#/profile" class="nav-link">
          <span class="emoji">👤</span>
          {$user?.username || 'Профиль'}
        </a>
        <button on:click={handleLogout} class="btn btn-outline btn-sm">Выйти</button>
      {:else}
        <a href="#/login" class="btn btn-primary btn-sm">Вход</a>
        <a href="#/register" class="btn btn-secondary btn-sm">Регистрация</a>
      {/if}
    </nav>
  </div>
</header>

<style>
  header {
    background: white;
    box-shadow: 0 4px 20px var(--shadow);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 16px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 12px;
    text-decoration: none;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-dark);
    transition: transform 0.3s ease;
  }

  .logo:hover {
    transform: scale(1.05);
  }

  .emoji {
    font-size: 1.8rem;
  }

  .title {
    background: linear-gradient(135deg, var(--primary-pink), var(--primary-green));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  nav {
    display: flex;
    align-items: center;
    gap: 20px;
  }

  .nav-link {
    text-decoration: none;
    color: var(--text-dark);
    font-weight: 500;
    transition: color 0.3s ease;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .nav-link:hover {
    color: var(--primary-pink);
  }

  .btn-sm {
    padding: 8px 16px;
    font-size: 0.9rem;
  }
</style>