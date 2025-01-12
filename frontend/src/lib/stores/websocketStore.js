import { writable } from 'svelte/store';
import { api } from '$lib/api';

function createWebsocketStore() {
    const { subscribe, set, update } = writable({
        connected: false,
        error: null,
        lastUpdate: null
    });

    let ws = null;
    let reconnectTimer = null;
    let currentRoomId = null;

    return {
        subscribe,
        connect: (roomId) => {
            currentRoomId = roomId;
            const token = localStorage.getItem('token');
            const wsUrl = `${api.getWebSocketUrl(roomId)}?token=${token}`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                console.log('WebSocket connected');
                update(store => ({ ...store, connected: true, error: null }));
            };
            
            ws.onerror = () => {
                console.error('WebSocket error');
                update(store => ({ ...store, error: 'Connection error' }));
            };
            
            ws.onclose = () => {
                console.log('WebSocket closed');
                update(store => ({ ...store, connected: false }));
                
                // Attempt to reconnect if we still have a room ID
                if (currentRoomId) {
                    reconnectTimer = setTimeout(() => {
                        console.log('Attempting to reconnect...');
                        this.connect(currentRoomId);
                    }, 5000);
                }
            };
        },
        disconnect: () => {
            currentRoomId = null;
            if (reconnectTimer) {
                clearTimeout(reconnectTimer);
            }
            if (ws) {
                ws.close();
                ws = null;
            }
        },
        setMessageHandler: (handler) => {
            if (ws) {
                ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        console.log('WebSocket message received:', data);
                        update(store => ({ ...store, lastUpdate: Date.now() }));
                        handler(data);
                    } catch (err) {
                        console.error('Error handling WebSocket message:', err);
                    }
                };
            }
        }
    };
}

export const websocketStore = createWebsocketStore(); 