import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { api } from '$lib/api';

function createUserStore() {
    const { subscribe, set, update } = writable(null);
    let initialized = false;
    let initializePromise = null;

    async function initialize() {
        if (initializePromise) return initializePromise;
        if (!browser) return Promise.resolve(null);
        
        initializePromise = (async () => {
            if (initialized) return;
            
            try {
                const token = localStorage.getItem('token');
                if (!token) {
                    set(null);
                    return null;
                }

                const userData = await api.getCurrentUser();
                set(userData);
                return userData;
            } catch (err) {
                console.error('Failed to initialize user:', err);
                // Clear invalid token
                localStorage.removeItem('token');
                set(null);
                return null;
            } finally {
                initialized = true;
                initializePromise = null;
            }
        })();

        return initializePromise;
    }

    // Initialize on creation if in browser
    if (browser) {
        initialize();
    }

    return {
        subscribe,
        set,
        update,
        initialize,
        login: async (email, password) => {
            const response = await api.login(email, password);
            const user = await api.getCurrentUser();
            set(user);
            return response;
        },
        logout: () => {
            if (browser) {
                localStorage.removeItem('token');
            }
            set(null);
        },
        updateUser: (userData) => {
            set(userData);
        }
    };
}

export const userStore = createUserStore();
