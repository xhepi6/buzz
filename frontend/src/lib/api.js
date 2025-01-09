const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function fetchApi(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'An error occurred');
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

export const api = {
  login: async (email, password) => {
    const formData = new URLSearchParams({ username: email, password });
    const response = await fetchApi('/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });
    localStorage.setItem('token', response.access_token);
    return response;
  },

  register: async (email, password, fullName, nickname) => {
    const response = await fetchApi('/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name: fullName, nickname }),
    });
    localStorage.setItem('token', response.access_token);
    return response;
  },

  getCurrentUser: async () => fetchApi('/me'),

  updateProfile: async (data) => fetchApi('/profile', {
    method: 'PUT',
    body: JSON.stringify(data),
  }),

  logout: () => localStorage.removeItem('token'),

  getGames: async (category = null) => fetchApi(category ? `/games?category=${category}` : '/games'),

  getGame: async (id) => fetchApi(`/games/${id}`),

  getCategories: async () => fetchApi('/categories'),

  createMafiaRoom: async (roomConfig) => fetchApi('/rooms', {
    method: 'POST',
    body: JSON.stringify({
      game_type: 'mafia',
      num_players: roomConfig.totalPlayers,
      game_config: {
        roles: roomConfig.roles,
        moderator: roomConfig.roles.moderator,
      },
    }),
  }),

  createSpyfallRoom: async (roomConfig) => fetchApi('/rooms/spyfall', {
    method: 'POST',
    body: JSON.stringify(roomConfig),
  }),


  getRoom: async (roomId) => {
    return await fetchApi(`/rooms/${roomId}`);
  },

  
  joinRoom: async (roomId, playerName) => fetchApi(`/rooms/${roomId}/join`, {
    method: 'POST',
    body: JSON.stringify({ playerName }),
  }),

  getGameState: async (roomId) => fetchApi(`/rooms/${roomId}/state`),

  getWebSocketUrl: (roomId) => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.host}/ws/${roomId}`;
  },
};
