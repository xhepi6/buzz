import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { api } from '$lib/api';

function createWebsocketStore() {
    const { subscribe, set, update } = writable({
        connected: false,
        error: null,
        lastUpdate: null,
        roomData: null,
        gameState: null
    });

    let ws = null;
    let reconnectTimer = null;
    let currentRoomId = null;
    let messageHandler = null;

    const store = {
        subscribe,
        connect: async (roomId) => {
            try {
                currentRoomId = roomId;
                const token = localStorage.getItem('token');
                if (!token) {
                    throw new Error('No authentication token found');
                }
                
                const wsUrl = `${api.getWebSocketUrl(roomId)}?token=${token}`;
                console.log('🔌 Attempting WebSocket connection to:', wsUrl);
                
                // Close existing connection if any
                if (ws) {
                    ws.close();
                    ws = null;
                }

                return new Promise((resolve, reject) => {
                    ws = new WebSocket(wsUrl);
                    
                    const timeout = setTimeout(() => {
                        if (ws) {
                            ws.close();
                            ws = null;
                        }
                        reject(new Error('WebSocket connection timeout'));
                    }, 5000);

                    ws.onopen = () => {
                        clearTimeout(timeout);
                        console.log('🔌 WebSocket connected successfully');
                        update(store => ({ ...store, connected: true, error: null }));
                        
                        if (messageHandler) {
                            ws.onmessage = messageHandler;
                        }
                        
                        resolve();
                    };

                    ws.onerror = (error) => {
                        clearTimeout(timeout);
                        console.error('❌ WebSocket error:', error);
                        update(store => ({ 
                            ...store, 
                            error: 'Connection error',
                            connected: false 
                        }));
                        reject(error);
                    };
                    
                    ws.onclose = (event) => {
                        console.log('🔌 WebSocket closed:', {
                            code: event.code,
                            reason: event.reason,
                            wasClean: event.wasClean
                        });
                        
                        update(store => ({ ...store, connected: false }));
                        
                        // Only attempt reconnection if we have a room ID and it wasn't a clean close
                        if (currentRoomId && !event.wasClean) {
                            console.log('🔄 Scheduling reconnection attempt...');
                            if (reconnectTimer) {
                                clearTimeout(reconnectTimer);
                            }
                            reconnectTimer = setTimeout(() => {
                                console.log('🔄 Attempting to reconnect...');
                                store.connect(currentRoomId).catch(err => {
                                    console.error('Reconnection failed:', err);
                                });
                            }, 5000);
                        }
                    };
                });
            } catch (error) {
                console.error('Failed to establish WebSocket connection:', error);
                throw error;
            }
        },
        
        disconnect: () => {
            console.log('🔌 Disconnecting WebSocket...');
            currentRoomId = null;
            messageHandler = null;
            
            if (reconnectTimer) {
                clearTimeout(reconnectTimer);
            }
            if (ws) {
                ws.close();
                ws = null;
            }
            update(store => ({ 
                ...store, 
                roomData: null,
                gameState: null,
                connected: false 
            }));
        },
        
        setMessageHandler: (handler) => {
            messageHandler = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('📨 WebSocket message received:', data);
                    
                    switch (data.type) {
                        case 'game_started':
                            sessionStorage.setItem('gameState', JSON.stringify(data.game_state));
                            update(store => ({
                                ...store,
                                gameState: data.game_state
                            }));
                            window.location.href = `/games/${data.game_type}/${data.room_code}`;
                            break;
                            
                        case 'room_update':
                            console.log('📦 Room update received:', data.room);
                            update(store => ({
                                ...store,
                                lastUpdate: Date.now(),
                                roomData: data.room
                            }));
                            break;
                            
                        case 'game_update':
                            update(store => ({
                                ...store,
                                gameState: {
                                    ...store.gameState,
                                    ...data.game_state
                                }
                            }));
                            break;

                        case 'game_ended':
                            console.log('🔚 Game ended:', data);
                            // Clear game state
                            sessionStorage.removeItem('gameState');
                            update(store => ({
                                ...store,
                                gameState: null
                            }));
                            // Redirect to room page
                            window.location.href = `/rooms/${data.room_code}`;
                            break;
                    }
                    
                    handler(data);
                } catch (err) {
                    console.error('❌ Error handling WebSocket message:', err);
                }
            };
            
            if (ws) {
                ws.onmessage = messageHandler;
            }
        }
    };

    return store;
}

export const websocketStore = createWebsocketStore(); 