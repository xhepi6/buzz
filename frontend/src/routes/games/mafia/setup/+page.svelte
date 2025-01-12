<!-- src/routes/games/mafia/setup/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import { userStore } from '$lib/stores/userStore';
    import { toastStore } from '$lib/stores/toastStore';
    
    let game = null;
    let loading = true;
    let error = null;
    let user = null;
    let showAuthModal = false;
    
    // Game setup state
    let totalPlayers = 4;
    let mafiaCount = 1;
    let hasDoctor = false;
    let hasPolice = false;
    let hasModerator = false;
    
    $: civilianCount = totalPlayers - mafiaCount - (hasPolice ? 1 : 0) - (hasDoctor ? 1 : 0);
    $: isValidSetup = civilianCount >= 0;
    
    userStore.subscribe(value => {
      user = value;
    });
    
    async function loadGame() {
      try {
        loading = true;
        // Load Mafia game details
        const games = await api.getGames();
        game = games.find(g => g.name.toLowerCase() === 'mafia');
        if (!game) throw new Error('Game not found');
      } catch (err) {
        error = err.message;
      } finally {
        loading = false;
      }
    }
    async function handleCreateRoom() {
        if (!user) {
            showAuthModal = true;
            return;
        }

        const roomConfig = {
            totalPlayers,
            roles: {
                mafia: mafiaCount,
                civilian: civilianCount,
                doctor: hasDoctor ? 1 : 0,
                police: hasPolice ? 1 : 0,
                moderator: hasModerator,
            },
        };

        try {
            const room = await api.createMafiaRoom(roomConfig);
            // Navigate to the room using the room code
            window.location.href = `/rooms/${room.code}`;
        } catch (err) {
            toastStore.error(err.message);
        }
    }
    onMount(() => {
      loadGame();
      userStore.init();
    });
  </script>
  
  <svelte:head>
    <title>Setup Mafia Game - Buzz!</title>
  </svelte:head>
  
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
      {:else}
        <div class="max-w-2xl mx-auto">
          <div class="text-center mb-12">
            <h1 class="text-5xl font-bold mb-4">
              <span class="text-cyber-primary">Setup</span>
              <span class="text-cyber-secondary">Mafia</span>
            </h1>
            <p class="text-cyber-primary/70">Configure your Mafia game session</p>
          </div>
          
          <div class="card bg-base-100/50 backdrop-blur shadow-xl p-6">
            <!-- Player Count -->
            <div class="form-control mb-6">
              <label class="label">
                <span class="label-text text-cyber-primary">Total Players</span>
                <span class="label-text-alt text-cyber-secondary">
                  4-12 players
                </span>
              </label>
              <input
                type="range"
                min="4"
                max="12"
                bind:value={totalPlayers}
                class="range range-primary"
              />
              <div class="text-center mt-2 text-cyber-primary">{totalPlayers} players</div>
            </div>
            
            <!-- Role Distribution -->
            <div class="form-control mb-6">
              <label class="label">
                <span class="label-text text-cyber-primary">Mafia Count</span>
              </label>
              <input
                type="range"
                min="1"
                max={Math.max(1, Math.floor(totalPlayers / 3))}
                bind:value={mafiaCount}
                class="range range-secondary"
              />
              <div class="text-center mt-2 text-cyber-secondary">{mafiaCount} mafia</div>
            </div>
            
            <!-- Special Roles -->
            <div class="flex flex-col gap-4 mb-6">
              <label class="label cursor-pointer justify-start gap-4">
                <input type="checkbox" class="checkbox checkbox-primary" bind:checked={hasDoctor} />
                <span class="label-text text-cyber-primary">Include Doctor</span>
              </label>
              
              <label class="label cursor-pointer justify-start gap-4">
                <input type="checkbox" class="checkbox checkbox-primary" bind:checked={hasPolice} />
                <span class="label-text text-cyber-primary">Include Police</span>
              </label>
              
              <label class="label cursor-pointer justify-start gap-4">
                <input type="checkbox" class="checkbox checkbox-primary" bind:checked={hasModerator} />
                <span class="label-text text-cyber-primary">Include Moderator</span>
              </label>
            </div>
            
            <!-- Role Summary -->
            <div class="bg-base-200/50 p-4 rounded-lg mb-6">
              <h3 class="text-lg font-bold text-cyber-primary mb-2">Role Distribution</h3>
              <ul class="space-y-2">
                <li class="text-cyber-secondary">Mafia: {mafiaCount}</li>
                <li class="text-cyber-primary">Civilians: {civilianCount}</li>
                {#if hasDoctor}<li class="text-cyber-accent">Doctor: 1</li>{/if}
                {#if hasPolice}<li class="text-cyber-accent">Police: 1</li>{/if}
              </ul>
            </div>
            
            <button
              class="btn btn-primary w-full"
              disabled={!isValidSetup}
              on:click={handleCreateRoom}
            >
              Create Room
            </button>
          </div>
        </div>
      {/if}
    </div>
  </div>
