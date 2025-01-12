<script>
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { userStore } from '$lib/stores/userStore';
  import { websocketStore } from '$lib/stores/websocketStore';
  import { api } from '$lib/api';
  import { browser } from '$app/environment';

  export const ssr = false;  // Disable SSR for game page

  let allLocations = [];
  let locationImages = {};
  let loading = true;
  let error = null;
  let user = null;
  let roleInfo = null;
  let isHost = false;
  let roomData = null;
  let roundEndTime = null;
  let timeRemaining = '';
  let timerInterval = null;

  // Get API URL from environment
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  function getFullImageUrl(path) {
    if (!path) return null;
    if (path.startsWith('http')) return path;
    if (path.startsWith('/static')) {
      return `${API_URL}${path}`;
    }
    return path;
  }

  // Add image loading state
  let imageLoading = true;
  let imageError = false;
  let debugImageData = null;

  // Fetch all locations when component mounts
  async function fetchLocations() {
    try {
      const game = await api.getGame('spyfall');
      locationImages = game.locations;
      allLocations = Object.keys(locationImages).sort();
    } catch (err) {
      console.error('Failed to fetch locations:', err);
    }
  }

  function updateTimeRemaining() {
    if (!roundEndTime) return;
    
    const now = new Date();
    const end = new Date(roundEndTime);
    const diff = end.getTime() - now.getTime();
    
    if (diff <= 0) {
      timeRemaining = "Time is up!";
      if (timerInterval) {
        clearInterval(timerInterval);
      }
      return;
    }
    
    const minutes = Math.floor(diff / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    timeRemaining = `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }

  function startTimer(endTime) {
    if (timerInterval) {
      clearInterval(timerInterval);
    }
    roundEndTime = endTime;
    updateTimeRemaining();
    timerInterval = setInterval(updateTimeRemaining, 1000);
  }

  async function handleRestart() {
    try {
      loading = true;
      await api.restartGame($page.params.code);
      // The WebSocket handler will handle the redirect
    } catch (err) {
      error = err.message;
      loading = false;
    }
  }

  function loadImage(url) {
    try {
        console.log('🔄 Loading image:', url);
        imageLoading = true;
        imageError = false;
        
        if (!url) {
            console.warn('⚠️ No image URL provided');
            imageError = true;
            imageLoading = false;
            return;
        }

        const img = new Image();
        img.onload = () => {
            console.log('✅ Image loaded successfully');
            debugImageData = {
                url: url,
                size: 'loaded',
                type: 'image',
                originalUrl: url
            };
            imageLoading = false;
        };
        img.onerror = (err) => {
            console.error('❌ Image load error:', err);
            imageError = true;
            imageLoading = false;
        };
        img.src = url;
    } catch (err) {
        console.error('❌ Error in loadImage:', err);
        imageError = true;
        imageLoading = false;
    }
  }

  onMount(async () => {
    try {
        loading = true;
        
        // Wait for user data with proper unsubscribe handling
        const userData = await new Promise((resolve) => {
            let unsubscribe = () => {};  // Initialize with empty function
            
            const handleUser = (value) => {
                if (value) {
                    unsubscribe();  // Clean up subscription
                    resolve(value);
                }
            };
            
            // Set up subscription and store unsubscribe function
            unsubscribe = userStore.subscribe(handleUser);
        });

        // Set user after promise resolves
        user = userData;
        
        // Get cached game state
        const cachedState = sessionStorage.getItem('gameState');
        if (cachedState) {
            const gameState = JSON.parse(cachedState);
            if (gameState.players) {
                const playerState = gameState.players.find(p => p.user_id === user?.id);
                if (playerState?.role_info) {
                    roleInfo = playerState.role_info;
                    if (roleInfo.location_image) {
                        loadImage(getFullImageUrl(roleInfo.location_image));
                    }
                    if (gameState.round_end_time) {
                        startTimer(gameState.round_end_time);
                    }
                }
            }
        }

        // If no role info from cache, try to get it from the room state
        if (!roleInfo) {
            try {
                const room = await api.getRoom($page.params.code);
                if (room.game_state?.players) {
                    const playerState = room.game_state.players.find(p => p.user_id === user?.id);
                    if (playerState?.role_info) {
                        roleInfo = playerState.role_info;
                        if (roleInfo.location_image) {
                            loadImage(getFullImageUrl(roleInfo.location_image));
                        }
                        if (room.game_state.round_end_time) {
                            startTimer(room.game_state.round_end_time);
                        }
                    }
                }
            } catch (err) {
                console.error('Failed to get room state:', err);
            }
        }

        // Fetch locations for reference
        await fetchLocations();

        // Connect to WebSocket
        await websocketStore.connect($page.params.code);
        
        // Set up message handler
        websocketStore.setMessageHandler((data) => {
            if (data.type === 'game_update') {
                if (data.event === 'role_assigned' && data.player_id === user?.id) {
                    roleInfo = data.role_info;
                    if (roleInfo.location_image) {
                        loadImage(getFullImageUrl(roleInfo.location_image));
                    }
                    if (data.game_state?.round_end_time) {
                        startTimer(data.game_state.round_end_time);
                    }
                }
            } else if (data.type === 'room_update' && data.room?.game_state?.players) {
                roomData = data.room;
                isHost = roomData.host === user?.id;
                
                // Update role info if not already set
                if (!roleInfo) {
                    const playerState = data.room.game_state.players.find(p => p.user_id === user?.id);
                    if (playerState?.role_info) {
                        roleInfo = playerState.role_info;
                        if (roleInfo.location_image) {
                            loadImage(getFullImageUrl(roleInfo.location_image));
                        }
                        if (data.room.game_state.round_end_time) {
                            startTimer(data.room.game_state.round_end_time);
                        }
                    }
                }
            }
        });

        loading = false;
    } catch (err) {
        error = err.message;
        loading = false;
    }
  });

  onDestroy(() => {
    if (timerInterval) {
      clearInterval(timerInterval);
    }
    websocketStore.disconnect();
    if (browser) {
      sessionStorage.removeItem('gameState');
    }
  });

  // Add the missing handleImageLoaded function
  function handleImageLoaded() {
    console.log('🖼️ Image rendered in DOM');
    imageLoading = false;
  }

  // ... rest of the component code (image handling, UI template) remains the same
</script>

<div class="min-h-screen bg-cyber-bg bg-gradient-to-b from-cyber-bg to-cyber-bg/50 pt-20">
  <div class="container mx-auto px-4">
    {#if loading}
      <div class="flex flex-col justify-center items-center py-12 min-h-[50vh]">
        <span class="loading loading-spinner loading-lg text-cyber-primary mb-4"></span>
        <span class="text-cyber-primary text-lg">Loading game state...</span>
      </div>
    {:else if error}
      <div class="alert alert-error mb-8">
        <span>{error}</span>
      </div>
    {:else if roleInfo}
      <div class="max-w-lg mx-auto">
        <div class="card bg-base-100/50 backdrop-blur shadow-xl border border-cyber-primary/20">
          <div class="p-6">
            <h2 class="text-2xl font-bold mb-4">
              <span class="text-cyber-primary">Your Role:</span>
              <span class="text-cyber-accent ml-2">{roleInfo.role}</span>
            </h2>
            
            <p class="text-cyber-secondary mb-6">{roleInfo.description}</p>
            
            {#if roleInfo.location}
              <div class="border-t border-cyber-primary/20 pt-4">
                <h3 class="text-lg font-semibold text-cyber-primary mb-2">Location:</h3>
                <p class="text-cyber-accent">{roleInfo.location}</p>
                
                {#if roleInfo.location_image}
                  <div class="relative aspect-video mt-4 bg-base-200 rounded-lg overflow-hidden">
                    {#if imageLoading}
                      <div class="absolute inset-0 flex items-center justify-center">
                        <span class="loading loading-spinner loading-lg text-cyber-primary"></span>
                      </div>
                    {/if}
                    
                    {#if debugImageData?.url}
                      <img
                        src={debugImageData.url}
                        alt="Location"
                        class="w-full h-full object-cover transition-opacity duration-300"
                        class:opacity-0={imageLoading}
                        class:opacity-100={!imageLoading}
                        on:load={handleImageLoaded}
                      />
                    {/if}
                    
                    {#if imageError}
                      <div class="absolute inset-0 flex items-center justify-center bg-base-200">
                        <div class="text-center text-cyber-secondary">
                          <span class="text-4xl">🖼️</span>
                          <p class="mt-2">Image not available</p>
                        </div>
                      </div>
                    {/if}
                  </div>
                {/if}
              </div>
            {/if}

            {#if timeRemaining}
              <div class="border-t border-cyber-primary/20 mt-4 pt-4">
                <h3 class="text-lg font-semibold text-cyber-primary mb-2">Time Remaining:</h3>
                <p class="text-cyber-accent text-xl">{timeRemaining}</p>
              </div>
            {/if}

            <!-- All Possible Locations -->
            <div class="border-t border-cyber-primary/20 mt-4 pt-4">
              <h3 class="text-lg font-semibold text-cyber-primary mb-2">All Possible Locations:</h3>
              <!-- 
                Version with thumbnails (current)
                To revert to text-only version:
                1. Remove locationImages object
                2. Replace this grid with:
                <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 text-sm">
                  {#each allLocations as location}
                    <div class="p-2 bg-base-200 rounded text-center text-cyber-secondary hover:bg-base-300 transition-colors">
                      {location}
                    </div>
                  {/each}
                </div>
              -->
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2 text-sm">
                {#each allLocations as location}
                  <div class="bg-base-200 rounded overflow-hidden hover:bg-base-300 transition-all hover:scale-105">
                    <div class="aspect-video w-full relative">
                      <img
                        src={getFullImageUrl(locationImages[location])}
                        alt={location}
                        class="w-full h-full object-cover"
                        loading="lazy"
                      />
                    </div>
                    <div class="p-1 text-center text-cyber-secondary text-xs">
                      {location}
                    </div>
                  </div>
                {/each}
              </div>
            </div>
          </div>
        </div>

        <!-- Sticky Restart Button for Host -->
        {#if isHost}
          <div class="fixed bottom-0 left-0 right-0 p-4 bg-base-300/80 backdrop-blur flex justify-center">
            <button 
              class="btn btn-primary w-full max-w-md"
              on:click={handleRestart}
            >
              Restart Game
            </button>
          </div>
          <!-- Spacer to prevent content from being hidden behind sticky button -->
          <div class="h-20"></div>
        {/if}
      </div>
    {:else}
      <div class="alert alert-warning">
        <span>No role information available. Please try refreshing the page.</span>
      </div>
    {/if}
  </div>
</div> 

<style>
  /* Add smooth transitions for image loading */
  img {
    transition: opacity 0.3s ease-in-out;
  }
  
  .aspect-video {
    aspect-ratio: 16 / 9;
    position: relative;
    overflow: hidden;
  }
</style> 