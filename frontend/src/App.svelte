<script>
  import Test from './routes/Test.svelte';
  import Router from 'svelte-spa-router';
  import { onMount } from 'svelte';
  import Header from './lib/components/Header.svelte';
  import Home from './routes/Home.svelte';
  import Login from './routes/Login.svelte';
  import Register from './routes/Register.svelte';
  import GamesList from './routes/GamesList.svelte';
  import CreateGame from './routes/CreateGame.svelte';
  import GameRoom from './routes/GameRoom.svelte';
  import Profile from './routes/Profile.svelte';
  import Leaderboard from './routes/Leaderboard.svelte';
  import { setUser, isAuthenticated } from './lib/stores/auth';
  import apiClient from './lib/utils/axios';

  const routes = {
    '/': Home,
    '/test': Test,
    '/login': Login,
    '/register': Register,
    '/games': GamesList,
    '/games/create': CreateGame,
    '/games/:id': GameRoom,
    '/profile': Profile,
    '/leaderboard': Leaderboard,
  };

  onMount(async () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const response = await apiClient.get('/users/me');
        setUser(response.data);
      } catch (error) {
        console.error('Failed to fetch user data');
      }
    }
  });
</script>

<div class="app">
  <Header />
  <main>
    <Router {routes} />
  </main>
</div>

<style>
  .app {
    min-height: 100vh;
  }

  main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 24px;
  }
</style>