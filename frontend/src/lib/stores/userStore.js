import { writable } from 'svelte/store';
import { api } from '$lib/api';

function createUserStore() {
    const { subscribe, set, update } = writable(null);

    return {
        subscribe,
        initialize: async () => {
            try {
                if (localStorage.getItem('token')) {
                    const user = await api.getCurrentUser();
                    set(user);
                    return user;
                }
                return null;
            } catch (error) {
                console.error('Failed to initialize user:', error);
                localStorage.removeItem('token');
                set(null);
                return null;
            }
        },
        setUser: (user) => {
            set(user);
        },
        clearUser: () => {
            set(null);
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
        updateProfile: async (data) => {
            const user = await api.updateProfile(data);
            set(user);
            return user;
        }
    };
}

export const userStore = createUserStore();

// Initialize the store when the module loads
userStore.initialize().catch(console.error);
