import { writable } from 'svelte/store';

export const gameUpdates = writable(null);

export function connectToGame(gameId, token) {
  const ws = new WebSocket(`ws://localhost:8000/api/v1/games/${gameId}/ws?token=${token}`);
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    gameUpdates.set(data);
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  return ws;
}