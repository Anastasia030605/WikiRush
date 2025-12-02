import { writable } from 'svelte/store';

export const currentGame = writable(null);
export const gameWebSocket = writable(null);
export const gameUpdates = writable(null);