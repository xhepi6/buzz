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
      if (response.status === 401) {
        throw new Error('401: Incorrect email or password');
      }
      if (response.status === 404) {
        throw new Error('404: Resource not found');
      }
      const error = await response.json();
      throw new Error(error.detail || `${response.status}: An error occurred`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

export const api = {
  login: async (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await fetchApi('/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });
    
    if (response.access_token) {
      localStorage.setItem('token', response.access_token);
      return response;
    }
    throw new Error('Invalid response from server');
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

  createMafiaRoom: async (roomConfig) => {
    const response = await fetchApi('/rooms', {
      method: 'POST',
      body: JSON.stringify({
        game_type: 'mafia',
        num_players: roomConfig.totalPlayers,
        game_config: {
          roles: roomConfig.roles,
          moderator: roomConfig.roles.moderator,
        },
      }),
    });
    console.log('Room creation response:', response);
    if (!response.code) {
      throw new Error('Invalid room response');
    }
    return response;
  },

  createSpyfallRoom: async (roomConfig) => {
    const response = await fetchApi('/rooms', {
      method: 'POST',
      body: JSON.stringify({
        game_type: 'spyfall',
        num_players: roomConfig.totalPlayers,
        game_config: {
          spyCount: roomConfig.settings.spyCount,
          roundMinutes: roomConfig.settings.roundMinutes,
          useCustomLocations: roomConfig.settings.useCustomLocations,
          customLocations: roomConfig.settings.customLocations
        }
      }),
    });
    if (!response.code) {
      throw new Error('Invalid room response');
    }
    return response;
  },

  getRoom: async (code) => {
    const response = await fetchApi(`/rooms/${code}`);
    return response;
  },

  joinRoom: async (code) => {
    const response = await fetchApi(`/rooms/${code}/join`, {
      method: 'POST',
    });
    return response;
  },

  getGameState: async (roomId) => fetchApi(`/rooms/${roomId}/state`),

  getWebSocketUrl: (roomId) => {
    const wsProtocol = API_BASE_URL.startsWith('https') ? 'wss:' : 'ws:';
    const apiUrl = new URL(API_BASE_URL);
    return `${wsProtocol}//${apiUrl.host}/ws/${roomId}`;
  },

  toggleReady: async (roomId) => fetchApi(`/rooms/${roomId}/ready`, {
    method: 'POST',
  }),

  leaveRoom: async (code) => {
    const response = await fetchApi(`/rooms/${code}/leave`, {
        method: 'POST'
    });
    return response;
  },

  startGame: async (code) => {
    const response = await fetchApi(`/rooms/${code}/start`, {
        method: 'POST'
    });
    return response;
  },

  restartGame: async (code) => {
    const response = await fetchApi(`/rooms/${code}/restart`, {
        method: 'POST'
    });
    return response;
  },
};
