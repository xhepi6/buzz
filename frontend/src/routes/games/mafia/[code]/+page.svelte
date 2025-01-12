<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { userStore } from '$lib/stores/userStore';
  import { websocketStore } from '$lib/stores/websocketStore';
  import RoleCard from '$lib/components/game-components/RoleCard.svelte';

  let game = null;
  let loading = true;
  let error = null;
  let user = null;
  let playerRole = null;

  userStore.subscribe(value => {
    user = value;
  });

  onMount(async () => {
    try {
      loading = true;
      // Only connect to WebSocket, no HTTP requests
      await websocketStore.connect($page.params.code);

      websocketStore.setMessageHandler((data) => {
        if (data.type === 'game_update') {
          console.log('🎮 Game update:', {
            type: data.type,
            event: data.event,
            playerId: data.player_id,
            currentUserId: user?.id,
            role: data.player_role
          });
          
          if (data.event === 'role_assigned' && data.player_id === user?.id) {
            console.log('🎭 Received role assignment:', data.player_role);
            playerRole = data.player_role;
            loading = false;
          }

          game = data.game;
        }
      });

    } catch (err) {
      console.error('Error in game page:', err);
      error = err.message;
      loading = false;
    }
  });

  onDestroy(() => {
    websocketStore.disconnect();
  });
</script>

<div class="min-h-screen bg-cyber-bg bg-gradient-to-b from-cyber-bg to-cyber-bg/50 pt-20">
  <div class="container mx-auto px-4">
    {#if loading}
      <div class="flex justify-center items-center py-12">
        <span class="loading loading-spinner loading-lg text-cyber-primary"></span>
      </div>
    {:else if error}
      <div class="alert alert-error mb-8">
        <span>{error}</span>
      </div>
    {:else if playerRole}
      <div class="max-w-lg mx-auto">
        <RoleCard 
          role={playerRole.role}
          description={playerRole.description}
          teammates={playerRole.teammates}
        />
      </div>
    {:else}
      <div class="flex justify-center items-center py-12">
        <span class="text-cyber-primary">Waiting for game to start...</span>
      </div>
    {/if}
  </div>
</div> 