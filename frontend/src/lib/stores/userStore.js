import { writable } from 'svelte/store';
import { api } from '../api';

function createUserStore() {
  const store = writable(null);
  const { subscribe, set } = store;

  return {
    subscribe,
    set,
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
      const response = await api.login(email, password);
      const user = await api.getCurrentUser();
      set(user);
      return response;
    },
    register: async (email, password, fullName, nickname) => {
      const response = await api.register(email, password, fullName, nickname);
      const user = await api.getCurrentUser();
      set(user);
      return response;
    },
    logout: () => {
      api.logout();
      set(null);
    },
    updateProfile: async (data) => {
      const user = await api.updateProfile(data);
      set(user);
      return user;
    }
  };
}

export const userStore = createUserStore();
