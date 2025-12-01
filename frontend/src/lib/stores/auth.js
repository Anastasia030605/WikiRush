import { writable } from 'svelte/store';

export const user = writable(null);
export const isAuthenticated = writable(false);

export function setUser(userData) {
  user.set(userData);
  isAuthenticated.set(true);
}

export function clearUser() {
  user.set(null);
  isAuthenticated.set(false);
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}