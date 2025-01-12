<script>
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { Crown, Share2 } from 'lucide-svelte';
  import { api } from '$lib/api';
  import { userStore } from '$lib/stores/userStore';
  import GameConfig from '$lib/components/GameConfig.svelte';

  let room = null;
  let loading = true;
  let error = null;
  let user = null;
  let ws = null;

  userStore.subscribe((value) => {
    user = value;
  });

  async function loadRoom() {
    try {
      const roomId = $page.params.id;
      room = await api.getRoom(roomId);
      loading = false;
    } catch (err) {
      error = err.message;
      loading = false;
    }
  }

  async function joinRoom() {
    try {
      const roomId = $page.params.id;
      room = await api.joinRoom(roomId);
      initWebSocket();
    } catch (err) {
      error = err.message;
    }
  }

  async function handleLeave() {
    try {
      const roomCode = $page.params.id;
      await api.leaveRoom(roomCode);
      window.location.href = '/';
    } catch (err) {
      toastStore.error(err.message);
    }
  }

  function initWebSocket() {
    const roomId = $page.params.id;
    const wsUrl = api.getWebSocketUrl(roomId);
    ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'room_update') {
        room = data.room;
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
    };
  }

  async function handleReady() {
    try {
      const roomId = $page.params.id;
      room = await api.toggleReady(roomId);
    } catch (err) {
      error = err.message;
    }
  }

  function handleShare() {
    navigator.clipboard.writeText(window.location.href);
  }

  $: totalPlayers = room?.num_players || 0;
  $: joinedPlayers = room?.players?.length || 0;
  $: readyPlayers = room?.players?.filter((p) => p.state === 'ready').length || 0;
  $: joinedPercentage = (joinedPlayers / totalPlayers) * 100;
  $: readyPercentage = (readyPlayers / totalPlayers) * 100;
  $: isInRoom = room?.players?.some((p) => p.user_id === user?.id) || false;
  $: isReady = room?.players?.find((p) => p.user_id === user?.id)?.state === 'ready';

  function getPlayerColor(nickname) {
    const colors = ['bg-blue-500', 'bg-purple-500', 'bg-pink-500', 'bg-indigo-500', 'bg-teal-500'];
    if (!nickname) return colors[0];
    const index = nickname.charCodeAt(0) % colors.length;
    return colors[index];
  }

  // Computed values for game start conditions
  $: isHost = user?.id === room?.host;
  $: allPlayersReady = room?.players?.every(p => p.state === "ready");
  $: canStartGame = isHost && allPlayersReady && joinedPlayers === totalPlayers;

  async function handleStartGame() {
    try {
      const roomCode = $page.params.id;
      const response = await api.startGame(roomCode);
      // The game state will be updated through WebSocket
      // You might want to redirect to the game page here
      window.location.href = `/games/${room.game_type}/${roomCode}`;
    } catch (err) {
      toastStore.error(err.message);
    }
  }

  onMount(async () => {
    await loadRoom();
    if (room && user && !room.players.some((p) => p.user_id === user.id)) {
      await joinRoom();
    }
    initWebSocket();
  });

  onDestroy(() => {
    if (ws) {
      ws.close();
    }
  });
</script>

<style>
  @keyframes pulse-slow {
    0%, 100% {
      transform: scale(1);
      opacity: 1;
    }
    50% {
      transform: scale(1.01);
      opacity: 0.9;
    }
  }
  
  .animate-pulse-slow {
    animation: pulse-slow 3s ease-in-out infinite;
  }
</style>

<div class="min-h-screen bg-cyber-bg bg-gradient-to-b from-cyber-bg to-cyber-bg/50 pt-20 flex flex-col">
  <div class="container mx-auto px-4 flex-1 overflow-y-auto">
    
    <!-- LOADING INDICATOR -->
    {#if loading}
      <div class="flex justify-center items-center py-12">
        <span class="loading loading-spinner loading-lg text-cyber-primary"></span>
      </div>

    <!-- ERROR ALERT -->
    {:else if error}
      <div class="alert alert-error mb-8">
        <span>{error}</span>
      </div>

    <!-- ROOM HEADER CARD -->
    {:else if room}
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

      <!-- PROGRESS BARS CARD -->
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

      <!-- GAME CONFIGURATION CARD -->
      <GameConfig gameType={room.game_type} config={room.game_config} />

      <!-- PLAYERS GRID CARD -->
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
                <span class="text-xs {player.state === 'ready' ? 'text-emerald-400' : 'text-cyber-secondary/50'}">
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
          class="btn btn-primary w-full font-medium"
          on:click={handleReady}
        >
          {isReady ? 'Not Ready' : 'Ready Up'}
        </button>
        <button 
          class="btn btn-secondary w-full font-medium"
          on:click={handleLeave}
        >
          Leave Room
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
            on:click={handleReady}
          >
            {isReady ? 'Not Ready' : 'Ready Up'}
          </button>
          <button 
            class="btn btn-secondary font-medium px-6"
            on:click={handleLeave}
          >
            Leave Room
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>
