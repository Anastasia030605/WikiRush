<script>
  import { push } from 'svelte-spa-router';
  import { isAuthenticated } from '../lib/stores/auth';

  function navigateTo(path) {
    push(path);
  }
</script>

<div class="home">
  <div class="hero">
    <h1>Добро пожаловать в WikiRush! 🏁</h1>
    <p class="subtitle">Игра-гонка по страницам Википедии</p>
    <p class="description">
      Найди кратчайший путь между статьями, переходя по ссылкам.
      Соревнуйся с друзьями или играй в одиночку!
    </p>
  </div>

  {#if $isAuthenticated}
    <div class="actions">
      <button class="btn btn-primary btn-lg" on:click={() => navigateTo('/create-game')}>
        Создать игру
      </button>
      <button class="btn btn-secondary btn-lg" on:click={() => navigateTo('/games')}>
        Список игр
      </button>
    </div>
  {:else}
    <div class="actions">
      <button class="btn btn-primary btn-lg" on:click={() => navigateTo('/register')}>
        Начать играть
      </button>
      <button class="btn btn-outline btn-lg" on:click={() => navigateTo('/login')}>
        Войти
      </button>
    </div>
  {/if}

  <div class="features">
    <div class="feature-card">
      <span class="feature-icon">⚡</span>
      <h3>Быстрая игра</h3>
      <p>Короткие раунды по 5-10 минут</p>
    </div>
    <div class="feature-card">
      <span class="feature-icon">👥</span>
      <h3>Мультиплеер</h3>
      <p>Соревнуйся с друзьями в реальном времени</p>
    </div>
    <div class="feature-card">
      <span class="feature-icon">🏆</span>
      <h3>Достижения</h3>
      <p>Собирай награды и прокачивай навыки</p>
    </div>
  </div>
</div>

<style>
  .home {
    text-align: center;
    padding: 60px 20px;
    max-width: 1200px;
    margin: 0 auto;
  }

  .hero {
    margin-bottom: 50px;
  }

  h1 {
    font-size: 3.5rem;
    color: var(--text-dark);
    margin-bottom: 20px;
    background: linear-gradient(135deg, var(--primary-pink), var(--primary-blue));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .subtitle {
    font-size: 1.5rem;
    color: var(--text-light);
    margin-bottom: 20px;
  }

  .description {
    font-size: 1.1rem;
    color: var(--text-light);
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.6;
  }

  .actions {
    display: flex;
    gap: 20px;
    justify-content: center;
    margin-bottom: 60px;
  }

  .btn-lg {
    padding: 18px 40px;
    font-size: 1.1rem;
    font-weight: 600;
  }

  .btn-outline {
    background: transparent;
    color: var(--primary-pink);
    border: 2px solid var(--primary-pink);
  }

  .btn-outline:hover {
    background: var(--light-pink);
  }

  .features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 30px;
    margin-top: 60px;
  }

  .feature-card {
    background: white;
    padding: 40px 30px;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }

  .feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
  }

  .feature-icon {
    font-size: 3rem;
    display: block;
    margin-bottom: 20px;
  }

  .feature-card h3 {
    font-size: 1.5rem;
    color: var(--text-dark);
    margin-bottom: 10px;
  }

  .feature-card p {
    color: var(--text-light);
    font-size: 1rem;
  }

  @media (max-width: 768px) {
    h1 {
      font-size: 2.5rem;
    }

    .subtitle {
      font-size: 1.2rem;
    }

    .actions {
      flex-direction: column;
      align-items: center;
    }

    .btn-lg {
      width: 100%;
      max-width: 300px;
    }

    .features {
      grid-template-columns: 1fr;
    }
  }
</style>