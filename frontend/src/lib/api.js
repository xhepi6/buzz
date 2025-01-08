const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function fetchApi(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

export const api = {
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

  // Room management (to be implemented with WebSocket)
  createRoom: async (gameId, playerName) => {
    return await fetchApi('/rooms', {
      method: 'POST',
      body: JSON.stringify({ gameId, playerName }),
    });
  },

  // Authentication
  login: async (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    return await fetchApi('/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });
  },

  register: async (email, password, name) => {
    return await fetchApi('/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    });
  },

  getCurrentUser: async () => {
    return await fetchApi('/me', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
  },
};
