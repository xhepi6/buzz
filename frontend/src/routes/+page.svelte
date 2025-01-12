<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import GameCard from '$lib/components/GameCard.svelte';
  import { goto } from '$app/navigation';
  import { userStore } from '$lib/stores/userStore';
  import AuthModal from '$lib/components/AuthModal.svelte';
  import { toastStore } from '$lib/stores/toastStore';

  let roomCode = '';
  let error = null;
  let showAuthModal = false;
  let showError = false;

  // Add type for featuredGames
  /** @type {Array<any>} */
  let featuredGames = [];
  let loadingFeaturedGames = true;
  /** @type {string|null} */
  let featuredGamesError = null;

  // Fetch featured games from the API
  async function loadFeaturedGames() {
    try {
      loadingFeaturedGames = true;
      featuredGames = await api.getGames();
    } catch (err) {
      featuredGamesError = err.message;
    } finally {
      loadingFeaturedGames = false;
    }
  }

  async function handleJoinRoom() {
    try {
      error = null;
      
      // Check if room code is provided
      if (!roomCode.trim()) {
        toastStore.warning("Please enter a room code");
        return;
      }

      // Check if user is authenticated using userStore
      if (!$userStore) {
        showAuthModal = true;
        return;
      }

      // Verify room exists before joining
      try {
        const room = await api.getRoom(roomCode);
        goto(`/rooms/${roomCode}`);
      } catch (error) {
        // Type the error properly
        const err = error instanceof Error ? error : new Error('Unknown error');
        if (err.message.includes('404') || err.message.includes('not found')) {
          toastStore.warning("Room not found. Please check the room code and try again.");
        } else {
          toastStore.error("Failed to join room. Please try again.");
        }
      }
    } catch (error) {
      const err = error instanceof Error ? error : new Error('Unknown error');
      toastStore.error(err.message);
    }
  }

  function handleCreateRoom() {
    goto('/games');
  }

  // Auto-hide error after 3 seconds
  $: if (showError) {
    setTimeout(() => {
      showError = false;
    }, 3000);
  }

  onMount(() => {
    loadFeaturedGames();
    userStore.init(); // Use userStore instead of authStore
  });
</script>

<svelte:head>
  <title>Buzz!</title>
</svelte:head>

<div class="min-h-screen bg-cyber-bg bg-gradient-to-b from-cyber-bg to-cyber-bg/50">
  <!-- Hero Section -->
  <div class="hero min-h-[70vh] relative overflow-hidden">
    <!-- Animated Background Elements -->
    <div class="absolute inset-0 overflow-hidden">
      <div class="absolute w-96 h-96 bg-cyber-primary/20 rounded-full blur-3xl -top-20 -left-20 animate-float"></div>
      <div class="absolute w-96 h-96 bg-cyber-secondary/20 rounded-full blur-3xl -bottom-20 -right-20 animate-float" style="animation-delay: -3s;"></div>
    </div>

    <div class="hero-content text-center z-10">
      <div class="max-w-md">
        <h1 class="text-6xl font-bold mb-8 tracking-wider">
          <span class="text-cyber-primary">BUZZ!</span>
          <span class="text-cyber-secondary">GAME</span>
          <span class="text-cyber-accent">HUB</span>
        </h1>
        <p class="mb-8 text-lg text-cyber-primary/80">Unite, play, and outsmart in social deduction and trivia games.</p>

        <div class="join join-vertical sm:join-horizontal w-full gap-2">
          <input
            class="input input-bordered input-lg join-item w-full bg-cyber-bg/50 border-cyber-primary text-cyber-primary placeholder-cyber-primary/50"
            placeholder="Enter Room Code"
            bind:value={roomCode}
          />
          <button 
            class="btn btn-primary btn-lg join-item animate-glow"
            on:click={handleJoinRoom}
          >
            Join Room
          </button>
        </div>

        <div class="divider text-cyber-primary/50">OR</div>

        <button
          class="btn btn-secondary btn-lg w-full sm:w-64 animate-glow"
          on:click={handleCreateRoom}
        >
          Create Room
        </button>
      </div>
    </div>
  </div>

  <!-- Featured Games -->
  <div class="container mx-auto px-4 py-16">
    <h2 class="text-3xl font-bold mb-8 text-center">
      <span class="text-cyber-primary">Featured</span>
      <span class="text-cyber-secondary">Games</span>
    </h2>

    {#if loadingFeaturedGames}
      <div class="flex justify-center items-center py-12">
        <span class="loading loading-spinner loading-lg text-cyber-primary"></span>
      </div>
    {:else if featuredGamesError}
      <div class="alert alert-error mb-8">
        <span>{featuredGamesError}</span>
      </div>
    {:else if featuredGames.length > 0}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {#each featuredGames as game (game.slug)}
          <GameCard {game} />
        {/each}
      </div>
    {:else}
      <div class="text-center py-12">
        <p class="text-cyber-primary/70">No featured games available</p>
      </div>
    {/if}
  </div>
</div>

<AuthModal
  isOpen={showAuthModal}
  message="You need to login first to join a game room."
  on:close={() => showAuthModal = false}
/>
