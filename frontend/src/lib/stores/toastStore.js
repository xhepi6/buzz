import { writable } from 'svelte/store';

function createToastStore() {
    const { subscribe, set, update } = writable([]);
    
    function addToast(message, type = 'error', duration = 3000) {
        const id = Math.random().toString(36).substr(2, 9);
        const toast = { id, message, type };
        
        update(toasts => [...toasts, toast]);
        
        if (duration) {
            setTimeout(() => {
                removeToast(id);
            }, duration);
        }
        
        return id;
    }
    
    function removeToast(id) {
        update(toasts => toasts.filter(t => t.id !== id));
    }
    
    return {
        subscribe,
        error: (msg) => addToast(msg, 'error'),
        success: (msg) => addToast(msg, 'success'),
        info: (msg) => addToast(msg, 'info'),
        warning: (msg) => addToast(msg, 'warning'),
        remove: removeToast,
        clear: () => set([])
    };
}

export const toastStore = createToastStore(); 