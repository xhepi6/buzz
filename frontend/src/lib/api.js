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
  // Authentication
  login: async (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetchApi('/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    localStorage.setItem('token', response.access_token);
    return response;
  },

  register: async (email, password, fullName, nickname) => {
    const response = await fetchApi('/register', {
      method: 'POST',
      body: JSON.stringify({ 
        email, 
        password, 
        full_name: fullName,
        nickname 
      }),
    });

    localStorage.setItem('token', response.access_token);
    return response;
  },

  getCurrentUser: async () => {
    return await fetchApi('/me');
  },

  updateProfile: async (data) => {
    return await fetchApi('/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  logout: () => {
    localStorage.removeItem('token');
  },

  // Games
  getGames: async (category = null) => {
    const url = category ? `/games?category=${category}` : '/games';
    return await fetchApi(url);
  },

  getGameDetails: async (gameId) => {
    return await fetchApi(`/games/${gameId}`);
  },

  getCategories: async () => {
    return await fetchApi('/categories');
  },

  // Room management
  createRoom: async (gameId, playerName) => {
    return await fetchApi('/rooms', {
      method: 'POST',
      body: JSON.stringify({ gameId, playerName }),
    });
  },

  joinRoom: async (roomId, playerName) => {
    return await fetchApi(`/rooms/${roomId}/join`, {
      method: 'POST',
      body: JSON.stringify({ playerName }),
    });
  },

  // Game state management
  getGameState: async (roomId) => {
    return await fetchApi(`/rooms/${roomId}/state`);
  },

  // WebSocket connection helper
  getWebSocketUrl: (roomId) => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = import.meta.env.VITE_WS_URL || `${wsProtocol}//${window.location.host}`;
    return `${wsHost}/ws/${roomId}`;
  }
};
