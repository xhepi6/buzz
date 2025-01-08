import { writable } from 'svelte/store';
import { api } from '../api';

function createGameStore() {
  const { subscribe, set, update } = writable({
    games: [],
    categories: [],
    loading: false,
    error: null,
  });

  return {
    subscribe,
    loadGames: async (category = null) => {
      update(state => ({ ...state, loading: true, error: null }));
      try {
        const games = await api.getGames(category);
        update(state => ({ ...state, games, loading: false }));
      } catch (error) {
        update(state => ({ ...state, error: error.message, loading: false }));
      }
    },
    loadCategories: async () => {
      try {
        const categories = await api.getCategories();
        update(state => ({ ...state, categories }));
      } catch (error) {
        update(state => ({ ...state, error: error.message }));
      }
    },
  };
}

export const gameStore = createGameStore();
