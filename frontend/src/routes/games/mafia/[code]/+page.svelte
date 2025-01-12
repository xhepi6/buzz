<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { userStore } from '$lib/stores/userStore';
  import { websocketStore } from '$lib/stores/websocketStore';
  import { api } from '$lib/api';

  export const ssr = false;  // Disable SSR for game page

  let loading = true;
  let error = null;
  let user = null;
  let roleInfo = null;
  let isHost = false;
  let roomData = null;
  let connectionAttempts = 0;
  const MAX_ATTEMPTS = 3;

  // Wait for user data to be available
  let userPromise = new Promise((resolve) => {
    userStore.subscribe(value => {
      user = value;
      if (value) {
        resolve(value);
      }
    });
  });

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

      // Get initial room data
      try {
        roomData = await api.getRoom($page.params.code);
        isHost = roomData.host === user?.id;
        console.log('🏠 Host check:', { isHost, userId: user?.id, hostId: roomData.host });
      } catch (err) {
        console.error('❌ Error getting room data:', err);
      }

      connectionAttempts++;
      await websocketStore.connect($page.params.code, 'game');
      console.log('🎮 Connected to game WebSocket');

      websocketStore.setMessageHandler((data) => {
        console.log('📨 Game message received:', data);
        
        // Handle role assignment
        if (data.type === 'game_update' && data.event === 'role_assigned') {
          console.log('🎭 Checking role assignment for user:', user?.id);
          console.log('🎭 Message player_id:', data.player_id);
          
          if (data.player_id === user?.id) {
            console.log('✅ Role assigned to current user:', data.role_info);
            roleInfo = data.role_info;
            loading = false;
          }
        }
        
        // Handle initial game state
        if (data.type === 'room_update') {
          roomData = data.room;
          isHost = roomData.host === user?.id;
          console.log('🏠 Updated host check:', { isHost, userId: user?.id, hostId: roomData.host });
          
          if (data.room?.game_state?.players) {
            console.log('🎮 Received game state update');
            const playerGameState = data.room.game_state.players.find(
              p => p.user_id === user?.id
            );
            
            if (playerGameState?.role_info) {
              console.log('✅ Found role in game state:', playerGameState.role_info);
              roleInfo = playerGameState.role_info;
              loading = false;
            }
          }
        }

        // Handle game ended event
        if (data.type === 'game_ended') {
          window.location.href = `/rooms/${$page.params.code}`;
        }
      });

    } catch (err) {
      console.error('❌ Error in game page:', err);
      if (connectionAttempts < MAX_ATTEMPTS) {
        console.log(`🔄 Retrying connection (attempt ${connectionAttempts + 1}/${MAX_ATTEMPTS})...`);
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
      console.log('🎮 Mounting game page, waiting for user data...');
      
      await userPromise;
      
      if (!user) {
        error = "User not authenticated";
        loading = false;
        return;
      }
      
      console.log('🎮 User data loaded:', user.id);
      await connectAndListen();
    } catch (err) {
      console.error('❌ Error in onMount:', err);
      error = err.message;
      loading = false;
    }
  });

  onDestroy(() => {
    console.log('🔌 Disconnecting from game WebSocket');
    websocketStore.disconnect();
  });

  $: {
    if (roleInfo) {
      console.log('🎭 Role info updated:', roleInfo);
    }
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
            
            {#if roleInfo.teammates && roleInfo.teammates.length > 0}
              <div class="border-t border-cyber-primary/20 pt-4">
                <h3 class="text-lg font-semibold text-cyber-primary mb-2">Your Team:</h3>
                <ul class="list-disc list-inside text-cyber-accent">
                  {#each roleInfo.teammates as teammate}
                    <li>{teammate}</li>
                  {/each}
                </ul>
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