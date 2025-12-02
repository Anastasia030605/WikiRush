import { writable } from 'svelte/store';

export function createGameWebSocket(gameId, token) {
  const updates = writable(null);
  const ws = new WebSocket(`ws://localhost:8000/api/v1/games/${gameId}/ws?token=${token}`);
  
  ws.onopen = () => {
    console.log('WebSocket connected');
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('WebSocket message:', data);
    updates.set(data);
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  ws.onclose = () => {
    console.log('WebSocket closed');
  };

  return {
    subscribe: updates.subscribe,
    close: () => ws.close(),
    send: (data) => ws.send(JSON.stringify(data))
  };
}