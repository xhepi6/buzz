<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import GameCard from '$lib/components/GameCard.svelte';
  import { gameStore } from '$lib/stores/gameStore';

  let games = [];
  let searchQuery = '';
  let selectedCategory = 'all';
  let loading = true;
  let error = null;

  async function loadGames(category = null) {
    try {
      loading = true;
      games = await api.getGames(category);
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  async function handleCategoryChange() {
    const category = selectedCategory === 'all' ? null : selectedCategory;
    await loadGames(category);
  }

  $: filteredGames = games.filter(game =>
    game.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  onMount(() => {
    loadGames();
  });
</script>

<svelte:head>
  <title>Buzz! - Games</title>
</svelte:head>

<div class="min-h-screen bg-cyber-bg bg-gradient-to-b from-cyber-bg to-cyber-bg/50 pt-20">
  <div class="container mx-auto px-4">
    <!-- Header Section -->
    <div class="text-center mb-12">
      <h1 class="text-5xl font-bold mb-4">
        <span class="text-cyber-primary">Game</span>
        <span class="text-cyber-secondary">Selection</span>
      </h1>
      <p class="text-cyber-primary/70">Choose your virtual battlefield</p>
    </div>

    <!-- Search and Filters -->
    <div class="flex flex-col md:flex-row gap-4 mb-8">
      <div class="relative flex-1">
        <input
          type="text"
          placeholder="Search games..."
          bind:value={searchQuery}
          class="input input-bordered w-full bg-cyber-bg/50 border-cyber-primary text-cyber-primary"
        />
      </div>

      <select
        bind:value={selectedCategory}
        on:change={handleCategoryChange}
        class="select select-bordered bg-cyber-bg/50 border-cyber-primary text-cyber-primary"
      >
        <option value="all">All Categories</option>
        {#each $gameStore.categories as category}
          <option value={category}>{category}</option>
        {/each}
      </select>
    </div>

    <!-- Loading State -->
    {#if loading}
      <div class="flex justify-center items-center py-12">
        <span class="loading loading-spinner loading-lg text-cyber-primary"></span>
      </div>
    {/if}

    <!-- Error State -->
    {#if error}
      <div class="alert alert-error mb-8">
        <span>{error}</span>
      </div>
    {/if}

    <!-- Games Grid -->
    {#if filteredGames.length > 0}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {#each filteredGames as game (game.id)}
          <GameCard {game} />
        {/each}
      </div>
    {:else if !loading}
      <div class="text-center py-12">
        <p class="text-cyber-primary/70">No games found matching your criteria</p>
      </div>
    {/if}
  </div>
</div>
