<script>
  export let game;
  const API_URL = import.meta.env.VITE_API_URL;

  function handleSelect() {
    window.location.href = `/lobby/new?game=${game.id}`;
  }
</script>

<div class="card bg-base-100/50 backdrop-blur shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105 animate-glow">
  <figure class="px-4 pt-4">
    {#if game.thumbnail_url}
      <img 
        src={`${API_URL}${game.thumbnail_url}`}
        alt={game.name} 
        class="rounded-xl h-48 w-full object-cover" 
      />
    {/if}
  </figure>
  <div class="card-body">
    <h2 class="card-title text-primary">{game.name}</h2>
    <div class="flex gap-2 flex-wrap">
      <div class="badge badge-secondary">{game.min_players}-{game.max_players} players</div>
      <div class="badge badge-accent">{game.duration_minutes}min</div>
      <div class="badge">{game.category}</div>
    </div>
    <p class="text-base-content/80">{game.description}</p>
    <div class="card-actions justify-end mt-4">
      <button class="btn btn-primary" on:click={handleSelect}>
        Select Game
      </button>
    </div>
  </div>
</div>
