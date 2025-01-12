<script>
  export const ssr = false;  // Disable SSR for room page
  
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { Crown, Share2 } from 'lucide-svelte';
  import { api } from '$lib/api';
  import { userStore } from '$lib/stores/userStore';
  import { websocketStore } from '$lib/stores/websocketStore';
  import GameConfig from '$lib/components/GameConfig.svelte';
  import { browser } from '$app/environment';

  let initialRoom = null;
  let loading = true;
  let error = null;
  let user = null;

  // Create a promise that resolves when user is loaded
  const userPromise = new Promise((resolve) => {
    let unsubscribe;
    
    function handleUser(value) {
      user = value;
      if (value) {
        if (unsubscribe) unsubscribe();
        resolve(value);
      } else if (browser) {
        // If we're in the browser and there's no user, try to initialize
        userStore.initialize().then(() => {
          if (!user) {
            if (unsubscribe) unsubscribe();
            resolve(null);
          }
        });
      }
    }

    // Set up the subscription
    unsubscribe = userStore.subscribe(handleUser);
  });

  $: room = $websocketStore.roomData || initialRoom;

  // Computed values
  $: totalPlayers = room?.num_players ?? 0;
  $: joinedPlayers = room?.players?.length ?? 0;
  $: readyPlayers = room?.players?.filter(p => p.state === 'ready').length ?? 0;
  $: joinedPercentage = (joinedPlayers / totalPlayers) * 100;
  $: readyPercentage = (readyPlayers / totalPlayers) * 100;
  $: isInRoom = room?.players?.some(p => p.user_id === user?.id) ?? false;
  $: currentPlayer = room?.players?.find(p => p.user_id === user?.id);
  $: isReady = currentPlayer?.state === 'ready' ?? false;
  $: isHost = user?.id === room?.host ?? false;
  $: allPlayersReady = room?.players?.every(p => p.state === "ready") ?? false;
  $: canStartGame = isHost && allPlayersReady && joinedPlayers === totalPlayers;

  function getPlayerColor(nickname) {
    const colors = ['bg-blue-500', 'bg-purple-500', 'bg-pink-500', 'bg-indigo-500', 'bg-teal-500'];
    if (!nickname) return colors[0];
    const index = nickname.charCodeAt(0) % colors.length;
    return colors[index];
  }

  async function handleReady(event) {
    if (event) event.preventDefault();
    
    try {
      loading = true;
      error = null;
      console.log('🔄 Toggling ready state...');
      
      await api.toggleReady($page.params.id);
      console.log('✅ Ready state toggled, waiting for WebSocket update');
      
    } catch (err) {
      console.error('❌ Error toggling ready state:', err);
      error = err.message;
    } finally {
      loading = false;
    }
  }

  async function handleLeave() {
    try {
        loading = true;
        error = null;
        
        await api.leaveRoom($page.params.id);
        // Disconnect WebSocket before navigating
        websocketStore.disconnect();
        // Navigate to home
        window.location.href = '/';
    } catch (err) {
        console.error('Failed to leave room:', err);
        error = err.message;
        loading = false;
    }
  }

  async function handleStartGame() {
    try {
        loading = true;
        error = null;
        
        await api.startGame($page.params.id);
        // Wait for game_started event via WebSocket
        console.log('✅ Game start request sent, waiting for confirmation...');
        
    } catch (err) {
        console.error('❌ Error starting game:', err);
        error = err.message;
        loading = false;
        
        // If unauthorized, try to refresh token or redirect to login
        if (err.message === 'Could not validate credentials') {
            window.location.href = '/';
        }
    }
  }

  function handleShare() {
    navigator.clipboard.writeText(window.location.href);
  }

  onMount(async () => {
    try {
        loading = true;

        // Wait for user to be loaded
        try {
            const userData = await userPromise;
            if (!userData) {
                error = "Please log in to continue";
                loading = false;
                return;
            }
        } catch (err) {
            console.error('Failed to load user:', err);
            error = "Failed to load user data";
            loading = false;
            return;
        }

        // Get initial room state
        try {
            initialRoom = await api.getRoom($page.params.id);
            
            // Check if user is not in room and join
            if (!initialRoom.players.some(p => p.user_id === user?.id)) {
                console.log('👤 Joining room as:', user.nickname);
                initialRoom = await api.joinRoom($page.params.id);
            }
        } catch (err) {
            console.error('Failed to load/join room:', err);
            error = "Failed to load room data";
            loading = false;
            return;
        }

        // Connect to WebSocket
        try {
            await websocketStore.connect($page.params.id);
            
            // Set up message handler
            websocketStore.setMessageHandler((data) => {
                switch (data.type) {
                    case 'room_update':
                        console.log('📦 Room update received:', data.room);
                        // Update both room and initialRoom to ensure reactivity
                        room = data.room;
                        initialRoom = data.room;
                        break;
                    case 'game_started':
                        // Game started, store will handle navigation
                        break;
                    case 'game_ended':
                        if (data.event === 'restart') {
                            window.location.reload();
                        }
                        break;
                }
            });
        } catch (wsError) {
            console.error('❌ WebSocket connection failed:', wsError);
            error = 'Failed to establish connection. Please refresh the page.';
            loading = false;
            return;
        }

        loading = false;
    } catch (err) {
        console.error('Error in room page:', err);
        error = err.message;
        loading = false;
    }
  });

  onDestroy(() => {
    websocketStore.disconnect();
  });
</script>

<div class="min-h-screen bg-cyber-bg bg-gradient-to-b from-cyber-bg to-cyber-bg/50 pt-20 flex flex-col">
  <div class="container mx-auto px-4 flex-1 overflow-y-auto">
    
    <!-- LOADING INDICATOR -->
    {#if loading}
      <div class="flex flex-col justify-center items-center py-12 min-h-[50vh]">
        <span class="loading loading-spinner loading-lg text-cyber-primary mb-4"></span>
        <span class="text-cyber-primary text-lg">Loading room...</span>
      </div>

    <!-- ERROR ALERT -->
    {:else if error}
      <div class="alert alert-error mb-8">
        <span>{error}</span>
      </div>

    <!-- ROOM CONTENT -->
    {:else if room}
      <!-- ROOM HEADER -->
      <div class="card bg-base-100/50 backdrop-blur shadow-xl border border-cyber-primary/20 mb-6">
        <div class="p-6">
          <div class="flex items-center">
            <h1 class="text-4xl font-bold mb-2 flex-1">
              <span class="text-cyber-primary">Game Room</span>
              <span class="text-cyber-secondary">#{room.code}</span>
            </h1>
            <button 
              class="btn btn-accent btn-outline ml-4 text-sm"
              on:click={handleShare}
            >
              <Share2 size="16" />
            </button>
          </div>
          <div class="flex items-center gap-3 text-sm mt-2">
            <span class="text-cyber-accent">{room.game_type}</span>
            <span class="text-cyber-primary/50">•</span>
            <span class="text-cyber-primary/70">
              {joinedPlayers}/{totalPlayers} Players
            </span>
          </div>
        </div>
      </div>

      <!-- PROGRESS BARS -->
      <div class="card bg-base-100/50 backdrop-blur shadow-xl border border-cyber-primary/20 mb-6">
        <div class="p-6 space-y-4">
          <h2 class="text-lg font-bold text-cyber-primary">Current Status</h2>
          <div class="relative h-4 bg-base-200 rounded-full overflow-hidden">
            <div 
              class="absolute h-full bg-orange-400/70 transition-all duration-500 ease-out"
              style="width: {joinedPercentage}%"
            ></div>
            <div 
              class="absolute h-full bg-emerald-500/80 transition-all duration-500 ease-out"
              style="width: {readyPercentage}%"
            ></div>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-cyber-secondary">{joinedPlayers} Joined</span>
            <span class="text-cyber-accent">{readyPlayers} Ready</span>
          </div>
        </div>
      </div>

      <!-- GAME CONFIG -->
      <GameConfig gameType={room.game_type} config={room.game_config} />

      <!-- PLAYERS GRID -->
      <div class="card bg-base-100/50 backdrop-blur shadow-xl border border-cyber-primary/20 mb-6">
        <div class="p-6">
          <h2 class="text-lg font-bold text-cyber-primary mb-4">Players</h2>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {#each room.players as player (player.user_id)}
              <div 
                class="relative bg-base-200/50 rounded-lg p-4 border 
                       {player.user_id === user?.id 
                         ? 'border-cyber-primary shadow-lg shadow-cyber-primary/10' 
                         : 'border-cyber-primary/10'} 
                       backdrop-blur-sm flex flex-col items-center
                       {player.user_id === user?.id && 'animate-pulse-slow'}"
              >
                <div class="w-12 h-12 rounded-full 
                            {getPlayerColor(player.nickname)} 
                            {player.user_id === user?.id && 'ring-2 ring-cyber-primary ring-offset-2 ring-offset-base-200/50'}
                            flex items-center justify-center text-xl font-bold text-white mb-2">
                  {player.nickname?.[0].toUpperCase() || '?'}
                </div>
                <span class="text-cyber-primary font-medium text-sm mb-1">
                  {player.nickname || 'Anonymous'}
                </span>
                <span 
                  class="text-xs transition-colors duration-300 
                         {player.state === 'ready' ? 'text-emerald-400' : 'text-cyber-secondary/50'}"
                >
                  {player.state === 'ready' ? 'Ready' : 'Not Ready'}
                </span>
                {#if player.user_id === room.host}
                  <div class="absolute top-2 right-2">
                    <Crown size={16} class="text-yellow-400" />
                  </div>
                {/if}
              </div>
            {/each}

            {#each Array(totalPlayers - joinedPlayers) as _, index (index)}
              <div 
                class="bg-base-200/20 rounded-lg p-4 border border-cyber-primary/10 
                       border-dashed flex flex-col items-center justify-center"
              >
                <div class="w-12 h-12 rounded-full bg-cyber-bg/10 flex items-center justify-center text-cyber-primary/50 mb-2">
                  ?
                </div>
                <span class="text-cyber-primary/50 text-sm">Empty Slot</span>
              </div>
            {/each}
          </div>
        </div>
      </div>
    {/if}

    <!-- Add spacer div at the bottom -->
    <div 
      class="h-[calc(3.5rem*3+1.5rem)] sm:h-[4.5rem]"
      class:h-[calc(3.5rem*2+1rem)]={!isHost}
    ></div>
  </div>

  <!-- STICKY BOTTOM ACTION BAR -->
  {#if room}
    <!-- Mobile buttons -->
    <div
      class="fixed bottom-0 left-0 w-full bg-base-100/90 border-t border-cyber-primary/20 
             backdrop-blur-sm shadow-xl py-3 px-4 sm:hidden"
      style="padding-bottom: max(env(safe-area-inset-bottom), 0.75rem);"
    >
      <div class="container mx-auto flex flex-col gap-3">
        {#if isHost}
          <button 
            class="btn btn-accent w-full font-medium"
            disabled={!canStartGame}
            on:click={handleStartGame}
          >
            {#if !allPlayersReady}
              Waiting for players...
            {:else if joinedPlayers !== totalPlayers}
              Waiting for more players...
            {:else}
              Start Game
            {/if}
          </button>
        {/if}
        <button 
          class="btn btn-primary font-medium px-6"
          on:click|preventDefault={handleReady}
          disabled={loading}
        >
          {#if loading}
            <span class="loading loading-spinner loading-sm"></span>
          {:else}
            {isReady ? 'Not Ready' : 'Ready Up'}
          {/if}
        </button>
        <button 
          class="btn btn-secondary font-medium px-6"
          on:click={handleLeave}
          disabled={loading}
        >
          {#if loading}
            <span class="loading loading-spinner loading-sm"></span>
          {:else}
            Leave Room
          {/if}
        </button>
      </div>
    </div>
    
    <!-- Desktop buttons -->
    <div 
      class="hidden sm:block fixed bottom-0 left-0 w-full bg-base-100/90 
             border-t border-cyber-primary/20 backdrop-blur-sm shadow-xl py-4"
    >
      <div class="container mx-auto px-4">
        <div class="flex gap-3 justify-center">
          {#if isHost}
            <button 
              class="btn btn-accent font-medium px-6"
              disabled={!canStartGame}
              on:click={handleStartGame}
            >
              {#if !allPlayersReady}
                Waiting for players...
              {:else if joinedPlayers !== totalPlayers}
                Waiting for more players...
              {:else}
                Start Game
              {/if}
            </button>
          {/if}
          <button 
            class="btn btn-primary font-medium px-6"
            on:click|preventDefault={handleReady}
            disabled={loading}
          >
            {#if loading}
              <span class="loading loading-spinner loading-sm"></span>
            {:else}
              {isReady ? 'Not Ready' : 'Ready Up'}
            {/if}
          </button>
          <button 
            class="btn btn-secondary font-medium px-6"
            on:click={handleLeave}
            disabled={loading}
          >
            {#if loading}
              <span class="loading loading-spinner loading-sm"></span>
            {:else}
              Leave Room
            {/if}
          </button>
        </div>
      </div>
    </div>
  {/if}

  <!-- WebSocket status indicator -->
  {#if $websocketStore.connected}
    <div class="fixed top-4 right-4 text-xs text-cyber-accent">
      Connected
    </div>
  {:else if $websocketStore.error}
    <div class="fixed top-4 right-4 text-xs text-error">
      Connection Error - Retrying...
    </div>
  {/if}

  <!-- Add a last update indicator -->
  {#if $websocketStore.lastUpdate}
    <div class="fixed top-4 left-4 text-xs text-cyber-secondary">
      Last update: {new Date($websocketStore.lastUpdate).toLocaleTimeString()}
    </div>
  {/if}
</div>
