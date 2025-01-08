<script>
    export let room;
    export let onJoin = () => {};
  
    function handleJoin() {
      onJoin(room.id);
    }
  </script>
  
  <div class="card bg-base-100/50 backdrop-blur shadow-xl">
    <div class="card-body">
      <h2 class="card-title text-primary">{room.name}</h2>
      <div class="flex gap-2">
        <div class="badge badge-secondary">{room.players.length}/{room.maxPlayers} Players</div>
        <div class="badge badge-accent">{room.game}</div>
      </div>
      <div class="flex gap-2 mt-2">
        {#each room.players as player}
          <div class="avatar placeholder">
            <div class="bg-neutral-focus text-neutral-content rounded-full w-8">
              <span class="text-xs">{player.name[0]}</span>
            </div>
          </div>
        {/each}
      </div>
      <div class="card-actions justify-end mt-4">
        <button class="btn btn-primary" on:click={handleJoin}>
          Join Room
        </button>
      </div>
    </div>
  </div>
