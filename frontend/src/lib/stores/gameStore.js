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


function createUserStore() {
  const { subscribe, set, update } = writable(null);

  return {
    subscribe,
    set,
    update,
    init: async () => {
      try {
        if (localStorage.getItem('token')) {
          const user = await api.getCurrentUser();
          set(user);
        }
      } catch (error) {
        console.error('Failed to initialize user:', error);
        localStorage.removeItem('token');
        set(null);
      }
    },
    login: async (email, password) => {
      await api.login(email, password);
      const user = await api.getCurrentUser();
      set(user);
    },
    register: async (email, password, fullName, nickname) => {
      await api.register(email, password, fullName, nickname);
      const user = await api.getCurrentUser();
      set(user);
    },
    logout: () => {
      api.logout();
      set(null);
    },
    updateProfile: async (data) => {
      const updatedUser = await api.updateProfile(data);
      set(updatedUser);
      return updatedUser;
    }
  };
}


export const userStore = createUserStore();
export const gameStore = createGameStore();
