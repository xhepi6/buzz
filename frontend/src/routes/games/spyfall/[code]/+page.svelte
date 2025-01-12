<script>
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { userStore } from '$lib/stores/userStore';
  import { websocketStore } from '$lib/stores/websocketStore';
  import { api } from '$lib/api';

  // Get API URL from environment
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  function getFullImageUrl(path) {
    if (!path) return null;
    // If it's already a full URL, return it
    if (path.startsWith('http')) return path;
    // If it starts with /static, prepend the API URL
    if (path.startsWith('/static')) {
      const fullUrl = `${API_URL}${path}`;
      console.log('🔍 Building full URL:', fullUrl);
      return fullUrl;
    }
    return path;
  }

  let loading = true;
  let error = null;
  let user = null;
  let roleInfo = null;
  let isHost = false;
  let roomData = null;
  let roundEndTime = null;
  let timeRemaining = '';
  let timerInterval = null;
  let connectionAttempts = 0;
  const MAX_ATTEMPTS = 3;

  let userPromise = new Promise((resolve) => {
    userStore.subscribe(value => {
      user = value;
      if (value) resolve(value);
    });
  });

  function updateTimeRemaining() {
    if (!roundEndTime) return;
    
    const now = new Date();
    const end = new Date(roundEndTime);
    const endUTC = new Date(Date.UTC(
      end.getUTCFullYear(),
      end.getUTCMonth(),
      end.getUTCDate(),
      end.getUTCHours(),
      end.getUTCMinutes(),
      end.getUTCSeconds()
    ));
    
    const nowUTC = new Date(Date.UTC(
      now.getUTCFullYear(),
      now.getUTCMonth(),
      now.getUTCDate(),
      now.getUTCHours(),
      now.getUTCMinutes(),
      now.getUTCSeconds()
    ));
    
    const diff = endUTC.getTime() - nowUTC.getTime();
    console.log('Time check:', {
      now: now.toISOString(),
      nowUTC: nowUTC.toISOString(),
      end: end.toISOString(),
      endUTC: endUTC.toISOString(),
      diff
    });
    
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
    console.log('Starting timer:', {
      endTime,
      currentTime: new Date().toISOString(),
      timezoneOffset: new Date().getTimezoneOffset()
    });
    roundEndTime = endTime;
    updateTimeRemaining();
    timerInterval = setInterval(updateTimeRemaining, 1000);
  }

  async function handleRestart() {
    try {
      loading = true;
      await api.restartGame($page.params.code);
      window.location.href = `/rooms/${$page.params.code}`;
    } catch (err) {
      error = err.message;
      loading = false;
    }
  }

  async function connectAndListen() {
    try {
      if (connectionAttempts >= MAX_ATTEMPTS) {
        error = "Failed to connect after multiple attempts";
        loading = false;
        return;
      }

      try {
        roomData = await api.getRoom($page.params.code);
        isHost = roomData.host === user?.id;
        if (roomData?.game_state?.round_end_time) {
          console.log('Initial timer setup:', {
            serverTime: roomData.game_state.round_end_time,
            localTime: new Date().toISOString(),
            diff: new Date(roomData.game_state.round_end_time) - new Date()
          });
          startTimer(roomData.game_state.round_end_time);
        }
      } catch (err) {
        console.error('❌ Error getting room data:', err);
      }

      connectionAttempts++;
      await websocketStore.connect($page.params.code, 'game');

      websocketStore.setMessageHandler((data) => {
        if (data.type === 'game_update' && data.event === 'role_assigned') {
          if (data.player_id === user?.id) {
            console.log('📦 Received role info:', data.role_info);
            console.log('🖼️ Location image path:', data.role_info.location_image);
            roleInfo = data.role_info;
            if (roleInfo.location_image) {
              console.log('🔄 Loading image from:', getFullImageUrl(roleInfo.location_image));
              loadImage(getFullImageUrl(roleInfo.location_image));
            } else {
              console.warn('⚠️ No location image in role info');
            }
            loading = false;
          }
        }
        
        if (data.type === 'room_update') {
          roomData = data.room;
          isHost = roomData.host === user?.id;
          
          if (data.room?.game_state?.players) {
            if (data.room?.game_state?.round_end_time) {
              console.log('⏰ Updating timer with new end time:', data.room.game_state.round_end_time);
              startTimer(data.room.game_state.round_end_time);
            }
            const playerGameState = data.room.game_state.players.find(
              p => p.user_id === user?.id
            );
            
            if (playerGameState?.role_info) {
              roleInfo = playerGameState.role_info;
              loading = false;
            }
          }
        }

        if (data.type === 'game_ended') {
          if (timerInterval) {
            clearInterval(timerInterval);
            timeRemaining = '';
          }
          window.location.href = `/rooms/${$page.params.code}`;
        }
      });

    } catch (err) {
      console.error('❌ Error in game page:', err);
      if (connectionAttempts < MAX_ATTEMPTS) {
        setTimeout(connectAndListen, 2000);
      } else {
        error = err.message;
        loading = false;
      }
    }
  }

  onMount(async () => {
    try {
      loading = true;
      await userPromise;
      
      if (!user) {
        error = "User not authenticated";
        loading = false;
        return;
      }
      
      await connectAndListen();
      
      // Verify image once roleInfo is available
      if (roleInfo?.location_image) {
        await verifyImage(getFullImageUrl(roleInfo.location_image));
      }
      
    } catch (err) {
      error = err.message;
      loading = false;
    }
  });

  onDestroy(() => {
    if (timerInterval) {
      clearInterval(timerInterval);
      timeRemaining = '';
    }
    websocketStore.disconnect();
  });

  // Add image loading state
  let imageLoading = true;
  let imageError = false;
  let debugImageData = null;

  async function verifyImage(url) {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const blob = await response.blob();
      // Create an object URL for debugging
      debugImageData = {
        url: URL.createObjectURL(blob),
        size: blob.size,
        type: blob.type,
        originalUrl: url
      };
      console.log('✅ Image verified:', debugImageData);
      return true;
    } catch (e) {
      console.error('❌ Image verification failed:', e);
      return false;
    }
  }

  function handleImageLoad() {
    imageLoading = false;
  }

  function handleImageError() {
    imageLoading = false;
    imageError = true;
  }

  // Function to load image
  async function loadImage(url) {
    try {
      console.log('🔄 Loading image:', url);
      imageLoading = true;
      const response = await fetch(url, {
        mode: 'cors',
        credentials: 'omit',
        headers: {
          'Accept': 'image/webp,image/*,*/*'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);
      console.log('✅ Image loaded:', { size: blob.size, type: blob.type, url: objectUrl });
      
      debugImageData = {
        url: objectUrl,
        size: blob.size,
        type: blob.type,
        originalUrl: url
      };

      imageError = false;
      return objectUrl;
    } catch (e) {
      console.error('❌ Image load error:', e);
      imageLoading = false;
      imageError = true;
      return null;
    }
  }

  // Add new function to handle image loaded in the DOM
  function handleImageLoaded() {
    console.log('🖼️ Image rendered in DOM');
    imageLoading = false;
  }
</script>

<div class="min-h-screen bg-cyber-bg bg-gradient-to-b from-cyber-bg to-cyber-bg/50 pt-20">
  <div class="container mx-auto px-4">
    {#if loading}
      <div class="flex justify-center items-center py-12">
        <span class="loading loading-spinner loading-lg text-cyber-primary"></span>
        <span class="ml-4 text-cyber-primary">Loading game state...</span>
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
                        class="w-full h-full object-cover transition-opacity duration-300 {imageLoading ? 'opacity-0' : 'opacity-100'}"
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
          </div>
        </div>

        {#if isHost}
          <div class="mt-6 flex justify-center">
            <button 
              class="btn btn-primary"
              on:click={handleRestart}
            >
              Restart Game
            </button>
          </div>
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