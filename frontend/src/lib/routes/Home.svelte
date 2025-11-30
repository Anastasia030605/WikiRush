<script>
  // @ts-ignore
  import { isAuthenticated } from '../lib/stores/auth';
</script>

<div class="home">
  <div class="hero">
    <div class="hero-content">
      <h1>
        <span class="emoji">🏁</span>
        Добро пожаловать в WikiRush!
      </h1>
      <p class="subtitle">Гонка по Википедии: найди кратчайший путь между статьями!</p>
      
      <div class="features">
        <div class="feature">
          <span class="feature-emoji">⚡</span>
          <h3>Быстрая игра</h3>
          <p>Соревнуйся с друзьями в реальном времени</p>
        </div>
        <div class="feature">
          <span class="feature-emoji">🎯</span>
          <h3>Стратегия</h3>
          <p>Выбирай правильные ссылки для победы</p>
        </div>
        <div class="feature">
          <span class="feature-emoji">🏆</span>
          <h3>Рейтинг</h3>
          <p>Поднимайся в таблице лидеров</p>
        </div>
      </div>

      <div class="cta-buttons">
        {#if $isAuthenticated}
          <a href="#/games/create" class="btn btn-primary btn-lg">Создать игру</a>
          <a href="#/games" class="btn btn-secondary btn-lg">Присоединиться</a>
        {:else}
          <a href="#/register" class="btn btn-primary btn-lg">Начать играть</a>
          <a href="#/login" class="btn btn-outline btn-lg">Уже есть аккаунт</a>
        {/if}
      </div>
    </div>

    <div class="hero-image">
      <div class="floating-card card-1">📖 → 🌍</div>
      <div class="floating-card card-2">🔗 ⚡ 🎯</div>
      <div class="floating-card card-3">🏆 🥇 ⭐</div>
    </div>
  </div>

  <div class="how-to-play">
    <h2>Как играть?</h2>
    <div class="steps">
      <div class="step">
        <div class="step-number">1</div>
        <h3>Создай или присоединись</h3>
        <p>Создай новую игру или присоединись к существующей</p>
      </div>
      <div class="step">
        <div class="step-number">2</div>
        <h3>Получи задание</h3>
        <p>Тебе дадут начальную и целевую статью</p>
      </div>
      <div class="step">
        <div class="step-number">3</div>
        <h3>Кликай по ссылкам</h3>
        <p>Переходи по ссылкам внутри статей</p>
      </div>
      <div class="step">
        <div class="step-number">4</div>
        <h3>Будь первым!</h3>
        <p>Первый, кто дойдёт до цели, побеждает</p>
      </div>
    </div>
  </div>
</div>

<style>
  .home {
    max-width: 1200px;
    margin: 0 auto;
  }

  .hero {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 60px;
    align-items: center;
    margin-bottom: 80px;
  }

  .hero-content h1 {
    font-size: 3rem;
    margin-bottom: 20px;
    line-height: 1.2;
  }

  .emoji {
    font-size: 3.5rem;
    display: block;
    margin-bottom: 10px;
  }

  .subtitle {
    font-size: 1.3rem;
    color: var(--text-light);
    margin-bottom: 40px;
  }

  .features {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-bottom: 40px;
  }

  .feature {
    text-align: center;
    padding: 20px;
    background: white;
    border-radius: 15px;
    box-shadow: 0 4px 15px var(--shadow);
  }

  .feature-emoji {
    font-size: 2.5rem;
    display: block;
    margin-bottom: 10px;
  }

  .feature h3 {
    font-size: 1.1rem;
    margin-bottom: 8px;
    color: var(--text-dark);
  }

  .feature p {
    font-size: 0.9rem;
    color: var(--text-light);
  }

  .cta-buttons {
    display: flex;
    gap: 20px;
  }

  .btn-lg {
    padding: 16px 32px;
    font-size: 1.1rem;
  }

  .hero-image {
    position: relative;
    height: 400px;
  }

  .floating-card {
    position: absolute;
    background: white;
    padding: 20px 30px;
    border-radius: 15px;
    font-size: 1.5rem;
    box-shadow: 0 8px 30px var(--shadow);
    animation: float 3s ease-in-out infinite;
  }

  .card-1 {
    top: 20%;
    left: 10%;
    background: linear-gradient(135deg, var(--light-pink), white);
    animation-delay: 0s;
  }

  .card-2 {
    top: 50%;
    right: 10%;
    background: linear-gradient(135deg, var(--light-green), white);
    animation-delay: 1s;
  }

  .card-3 {
    bottom: 10%;
    left: 30%;
    background: linear-gradient(135deg, var(--secondary-pink), var(--secondary-green));
    animation-delay: 2s;
  }

  @keyframes float {
    0%, 100% {
      transform: translateY(0);
    }
    50% {
      transform: translateY(-20px);
    }
  }

  .how-to-play {
    text-align: center;
    padding: 60px 0;
  }

  .how-to-play h2 {
    font-size: 2.5rem;
    margin-bottom: 50px;
  }

  .steps {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 30px;
  }

  .step {
    background: white;
    padding: 30px 20px;
    border-radius: 20px;
    box-shadow: 0 8px 30px var(--shadow);
    transition: transform 0.3s ease;
  }

  .step:hover {
    transform: translateY(-10px);
  }

  .step-number {
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, var(--primary-pink), var(--primary-green));
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0 auto 20px;
  }

  .step h3 {
    font-size: 1.2rem;
    margin-bottom: 10px;
    color: var(--text-dark);
  }

  .step p {
    color: var(--text-light);
  }

  @media (max-width: 768px) {
    .hero {
      grid-template-columns: 1fr;
    }

    .hero-image {
      display: none;
    }

    .features, .steps {
      grid-template-columns: 1fr;
    }

    .hero-content h1 {
      font-size: 2rem;
    }
  }
</style>