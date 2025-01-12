<script>
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { Crown } from 'lucide-svelte';
  import { api } from '$lib/api';
  import { userStore } from '$lib/stores/userStore';

  let room = null;
  let loading = true;
  let error = null;
  let user = null;
  let ws = null;

  // Subscribe to user store
  userStore.subscribe(value => {
    user = value;
  });

  // Fetch room data
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

  // Join room function
  async function joinRoom() {
    try {
      const roomId = $page.params.id;
      room = await api.joinRoom(roomId);
      initWebSocket(); // Initialize WebSocket after joining
    } catch (err) {
      error = err.message;
    }
  }

  // Initialize WebSocket connection
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

  // Toggle ready state
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
    // You could add a toast notification here
  }

  // Calculate progress percentages
  $: totalPlayers = room?.num_players || 0;
  $: joinedPlayers = room?.players?.length || 0;
  $: readyPlayers = room?.players?.filter(p => p.state === "ready").length || 0;
  $: joinedPercentage = (joinedPlayers / totalPlayers) * 100;
  $: readyPercentage = (readyPlayers / totalPlayers) * 100;

  // Check if current user is in the room
  $: isInRoom = room?.players?.some(p => p.user_id === user?.id) || false;
  $: isReady = room?.players?.find(p => p.user_id === user?.id)?.state === "ready";

  // Generate background color based on name
  function getPlayerColor(nickname) {
    const colors = ['bg-blue-500', 'bg-purple-500', 'bg-pink-500', 'bg-indigo-500', 'bg-teal-500'];
    if (!nickname) return colors[0];
    const index = nickname.charCodeAt(0) % colors.length;
    return colors[index];
  }

  onMount(async () => {
    await loadRoom();
    // Only try to join if user isn't already in the room
    if (room && user && !room.players.some(p => p.user_id === user.id)) {
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

<div class="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 p-4 pt-24">
  <div class="max-w-lg mx-auto space-y-6">
    {#if loading}
      <div class="flex justify-center items-center py-12">
        <span class="loading loading-spinner loading-lg text-primary"></span>
      </div>
    {:else if error}
      <div class="alert alert-error mb-8">
        <span>{error}</span>
      </div>
    {:else if room}
      <!-- Header -->
      <div class="bg-gray-800/50 rounded-lg p-6 backdrop-blur-sm border border-gray-700">
        <h1 class="text-2xl font-bold text-white mb-2">
            Game Room #{room.code}
        </h1>
        <div class="flex items-center space-x-2">
          <span class="text-emerald-400">{room.game_type}</span>
          <span class="text-gray-400">•</span>
          <span class="text-gray-400">{joinedPlayers}/{totalPlayers} Players</span>
        </div>
      </div>

      <!-- Progress Bars -->
      <div class="bg-gray-800/50 rounded-lg p-6 backdrop-blur-sm border border-gray-700">
        <div class="space-y-4">
          <div class="relative h-4 bg-gray-700 rounded-full overflow-hidden">
            <div 
              class="absolute h-full bg-blue-500 transition-all duration-500 ease-out"
              style="width: {joinedPercentage}%"
            />
            <div 
              class="absolute h-full bg-emerald-500 transition-all duration-500 ease-out"
              style="width: {readyPercentage}%"
            />
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-blue-400">{joinedPlayers} Joined</span>
            <span class="text-emerald-400">{readyPlayers} Ready</span>
          </div>
        </div>
      </div>

      <!-- Players Grid -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {#each room.players as player (player.user_id)}
          <div 
            class="relative bg-gray-800/50 rounded-lg p-4 backdrop-blur-sm border border-gray-700 flex flex-col items-center"
          >
            <div class="w-12 h-12 rounded-full {getPlayerColor(player.nickname)} flex items-center justify-center text-xl font-bold text-white mb-2">
              {player.nickname?.[0].toUpperCase() || '?'}
            </div>
            <span class="text-white font-medium text-sm mb-1">{player.nickname || 'Anonymous'}</span>
            <span class="text-xs {player.state === 'ready' ? 'text-emerald-400' : 'text-gray-400'}">
              {player.state === 'ready' ? 'Ready' : 'Not Ready'}
            </span>
            {#if player.user_id === room.host}
              <div class="absolute top-2 right-2">
                <Crown size={16} class="text-yellow-400" />
              </div>
            {/if}
          </div>
        {/each}
        
        <!-- Empty Slots -->
        {#each Array(totalPlayers - joinedPlayers) as _, index (index)}
          <div 
            class="bg-gray-800/20 rounded-lg p-4 border border-gray-700/50 border-dashed flex flex-col items-center"
          >
            <div class="w-12 h-12 rounded-full bg-gray-700/30 flex items-center justify-center text-gray-500 mb-2">
              ?
            </div>
            <span class="text-gray-500 text-sm">Empty Slot</span>
          </div>
        {/each}
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-col sm:flex-row gap-3 mt-6">
        <button 
          class="btn flex-1 bg-emerald-500 hover:bg-emerald-600 text-white font-medium py-3 px-6 rounded-lg transition-colors"
          on:click={handleReady}
        >
          {isReady ? 'Not Ready' : 'Ready Up'}
        </button>
        <button 
          class="btn flex-1 bg-blue-500 hover:bg-blue-600 text-white font-medium py-3 px-6 rounded-lg transition-colors"
          on:click={handleShare}
        >
          Share Room
        </button>
      </div>
    {/if}
  </div>
</div>