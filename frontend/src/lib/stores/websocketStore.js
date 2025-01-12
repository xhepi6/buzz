import { writable } from 'svelte/store';
import { api } from '$lib/api';

function createWebsocketStore() {
    const { subscribe, set, update } = writable({
        connected: false,
        error: null,
        lastUpdate: null,
        roomData: null
    });

    let ws = null;
    let reconnectTimer = null;
    let currentRoomId = null;
    let messageHandler = null; // Store the message handler

    return {
        subscribe,
        connect: async (roomId) => {
            currentRoomId = roomId;
            const token = localStorage.getItem('token');
            const wsUrl = `${api.getWebSocketUrl(roomId)}?token=${token}`;
            
            console.log('🔌 Attempting WebSocket connection to:', wsUrl);
            
            return new Promise((resolve, reject) => {
                ws = new WebSocket(wsUrl);
                
                const timeout = setTimeout(() => {
                    reject(new Error('WebSocket connection timeout'));
                }, 5000);

                ws.onopen = () => {
                    clearTimeout(timeout);
                    console.log('🔌 WebSocket connected successfully');
                    update(store => ({ ...store, connected: true, error: null }));
                    
                    // Set message handler after connection if one was provided
                    if (messageHandler && ws) {
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
                    
                    if (currentRoomId) {
                        console.log('🔄 Scheduling reconnection attempt...');
                        reconnectTimer = setTimeout(() => {
                            console.log('🔄 Attempting to reconnect...');
                            this.connect(currentRoomId);
                        }, 5000);
                    }
                };
            });
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
                connected: false 
            }));
        },
        
        setMessageHandler: (handler) => {
            // Create wrapper for the message handler
            messageHandler = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('📨 WebSocket message received:', data);
                    
                    if (data.type === 'room_update') {
                        update(store => ({
                            ...store,
                            lastUpdate: Date.now(),
                            roomData: {
                                ...store.roomData,
                                ...data.room,
                                players: data.players || data.room.players
                            }
                        }));
                    }
                    
                    handler(data);
                } catch (err) {
                    console.error('❌ Error handling WebSocket message:', err);
                }
            };
            
            // If we already have a connection, set the handler immediately
            if (ws) {
                ws.onmessage = messageHandler;
            } else {
                console.log('⏳ Message handler stored for when connection is established');
            }
        }
    };
}

export const websocketStore = createWebsocketStore(); 