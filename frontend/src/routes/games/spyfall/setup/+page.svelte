<!-- src/routes/games/spyfall/setup/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import AuthModal from '$lib/components/AuthModal.svelte';
    import { userStore } from '$lib/stores/userStore';
    
    let game = null;
    let loading = true;
    let error = null;
    let showAuthModal = false;
    let user = null;
    
    // Game setup state
    let totalPlayers = 4;
    let roundMinutes = 8;
    let spyCount = 1;
    let useCustomLocations = false;
    let customLocationsText = '';
    $: customLocations = customLocationsText.split('\n').filter(Boolean);
    
    // Computed values
    $: isValidSetup = totalPlayers >= game?.min_players && 
                      totalPlayers <= game?.max_players && 
                      spyCount < totalPlayers / 2;
    
    userStore.subscribe(value => {
      user = value;
    });
    
    async function loadGame() {
      try {
        loading = true;
        // Load Spyfall game details
        const games = await api.getGames();
        game = games.find(g => g.slug === 'spyfall');
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
        gameId: game.id,
        totalPlayers,
        settings: {
          roundMinutes,
          spyCount,
          useCustomLocations,
          customLocations
        }
      };
      
      try {
        const room = await api.createSpyfallRoom(roomConfig);
        window.location.href = `/rooms/${room._id}`;
      } catch (err) {
        error = err.message;
      }
    }
    
    onMount(() => {
      loadGame();
      userStore.init();
    });
  </script>
  
  <svelte:head>
    <title>Setup Spyfall Game - Buzz!</title>
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
              <span class="text-cyber-secondary">Spyfall</span>
            </h1>
            <p class="text-cyber-primary/70">Configure your Spyfall game session</p>
          </div>
          
          <div class="card bg-base-100/50 backdrop-blur shadow-xl p-6">
            <!-- Player Count -->
            <div class="form-control mb-6">
              <label class="label">
                <span class="label-text text-cyber-primary">Total Players</span>
                <span class="label-text-alt text-cyber-secondary">
                  {game.min_players}-{game.max_players} players
                </span>
              </label>
              <input
                type="range"
                min={game.min_players}
                max={game.max_players}
                bind:value={totalPlayers}
                class="range range-primary"
              />
              <div class="text-center mt-2 text-cyber-primary">{totalPlayers} players</div>
            </div>
            
            <!-- Spy Count -->
            <div class="form-control mb-6">
              <label class="label">
                <span class="label-text text-cyber-primary">Number of Spies</span>
              </label>
              <input
                type="range"
                min="1"
                max={Math.floor(totalPlayers / 2) - 1}
                bind:value={spyCount}
                class="range range-secondary"
              />
              <div class="text-center mt-2 text-cyber-secondary">{spyCount} {spyCount === 1 ? 'spy' : 'spies'}</div>
            </div>
            
            <!-- Round Duration -->
            <div class="form-control mb-6">
              <label class="label">
                <span class="label-text text-cyber-primary">Round Duration (minutes)</span>
              </label>
              <input
                type="range"
                min="5"
                max="15"
                step="1"
                bind:value={roundMinutes}
                class="range range-accent"
              />
              <div class="text-center mt-2 text-cyber-accent">{roundMinutes} minutes</div>
            </div>
            
            <!-- Custom Locations -->
            <div class="form-control mb-6">
              <label class="label cursor-pointer justify-start gap-4">
                <input 
                  type="checkbox" 
                  class="checkbox checkbox-primary" 
                  bind:checked={useCustomLocations}
                />
                <span class="label-text text-cyber-primary">Use Custom Locations</span>
              </label>
              
              {#if useCustomLocations}
                <div class="mt-4">
                  <textarea
                    class="textarea textarea-bordered w-full h-32 bg-base-200/50"
                    placeholder="Enter custom locations (one per line)"
                    bind:value={customLocationsText}
                  />
                </div>
              {/if}
            </div>
            
            <!-- Game Summary -->
            <div class="bg-base-200/50 p-4 rounded-lg mb-6">
              <h3 class="text-lg font-bold text-cyber-primary mb-2">Game Settings</h3>
              <ul class="space-y-2">
                <li class="text-cyber-secondary">Players: {totalPlayers}</li>
                <li class="text-cyber-secondary">Spies: {spyCount}</li>
                <li class="text-cyber-accent">Round Duration: {roundMinutes} minutes</li>
                {#if useCustomLocations}
                  <li class="text-cyber-accent">Custom Locations: {customLocations.length}</li>
                {/if}
              </ul>
            </div>
            
            <button
              class="btn btn-primary w-full"
              disabled={!isValidSetup}
              on:click={handleCreateRoom}
            >
              Create Room
            </button>
            
            {#if !isValidSetup}
              <p class="text-error text-sm mt-2">
                Please ensure valid player counts and at least one spy.
              </p>
            {/if}
          </div>
        </div>
      {/if}
    </div>
  </div>
  
  <AuthModal
    isOpen={showAuthModal}
    on:close={() => showAuthModal = false}
  />
