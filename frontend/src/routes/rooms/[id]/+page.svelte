<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { api } from '$lib/api';

  let room = null;
  let messages = [];
  let newMessage = '';
  let showSettingsModal = false;
  let copyLinkTooltip = 'Copy Link';
  let loading = true;
  let error = null;

  // Placeholder for avatar generation
  function generateAvatar(userId) {
    return `/api/placeholder/100/100`;
  }

  // Function to get player name from ID (in real app, might come from user service)
  function getPlayerName(userId) {
    const names = {
      "78229a44-faf1-4931-b39b-778226ae8a6a": "CyberRunner",
      // Add more mappings as needed
    };
    return names[userId] || userId.slice(0, 8);
  }

  async function loadRoomDetails() {
    try {
      const roomId = $page.params.id;
      room = await api.getRoom(roomId);
      loading = false;
    } catch (err) {
      error = err.message;
      loading = false;
    }
  }

  function handleSendMessage() {
    if (newMessage.trim()) {
      messages = [...messages, {
        id: Date.now(),
        text: newMessage,
        sender: 'You',
        timestamp: new Date().toLocaleTimeString()
      }];
      newMessage = '';
    }
  }

  function copyRoomLink() {
    navigator.clipboard.writeText(window.location.href);
    copyLinkTooltip = 'Copied!';
    setTimeout(() => copyLinkTooltip = 'Copy Link', 2000);
  }

  function toggleReady() {
    // Implement ready state toggle logic here
    console.log('Toggle ready state');
  }

  onMount(() => {
    loadRoomDetails();
  });
</script>

<svelte:head>
  <title>Buzz! - Game Lobby</title>
</svelte:head>

<div class="min-h-screen bg-cyber-bg bg-gradient-to-b from-cyber-bg to-cyber-bg/50 pt-20">
  {#if loading}
    <div class="flex justify-center items-center h-[60vh]">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>
  {:else if error}
    <div class="container mx-auto p-4">
      <div class="alert alert-error">
        <span>{error}</span>
      </div>
    </div>
  {:else if room}
    <div class="container mx-auto p-4">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Main Game Area -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Room Info -->
          <div class="card bg-base-100/50 backdrop-blur shadow-xl border border-primary/20">
            <div class="card-body">
              <div class="flex justify-between items-center">
                <div>
                  <h2 class="card-title text-2xl text-primary">Cyber Room #{room._id.slice(-4)}</h2>
                  <div class="badge badge-secondary mt-2">{room.game_type}</div>
                </div>
                <img
                  src="/api/placeholder/128/128"
                  alt={room.game_type}
                  class="w-32 h-32 object-cover rounded-lg border border-primary/20"
                />
              </div>

              <!-- Game Status -->
              <div class="mt-4 flex flex-wrap gap-4">
                <div class="stat bg-base-300/30 rounded-box p-4 flex-1">
                  <div class="stat-title text-primary/70">Players</div>
                  <div class="stat-value text-primary">{room.players.length}/{room.num_players}</div>
                </div>
                <div class="stat bg-base-300/30 rounded-box p-4 flex-1">
                  <div class="stat-title text-primary/70">Game Type</div>
                  <div class="stat-value text-accent capitalize">{room.game_type}</div>
                </div>
              </div>

              <!-- Role Distribution -->
              {#if room.game_config?.roles}
                <div class="mt-4">
                  <h3 class="text-lg font-semibold text-primary mb-2">Role Distribution</h3>
                  <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                    {#each Object.entries(room.game_config.roles) as [role, count]}
                      <div class="badge badge-outline badge-lg gap-2">
                        {role}: {count}
                      </div>
                    {/each}
                  </div>
                </div>
              {/if}
            </div>
          </div>

          <!-- Players Grid -->
          <div class="card bg-base-100/50 backdrop-blur shadow-xl border border-primary/20">
            <div class="card-body">
              <h3 class="text-xl font-bold text-primary mb-4">Players</h3>
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {#each room.players as player}
                  <div class="card bg-base-300/30 hover:bg-base-300/40 transition-all">
                    <div class="card-body p-4 text-center">
                      <div class="avatar mb-2">
                        <div class="w-16 h-16 rounded-full ring ring-primary/30 ring-offset-base-100 ring-offset-2">
                          <img src={generateAvatar(player.user_id)} alt={getPlayerName(player.user_id)} />
                        </div>
                      </div>
                      <h4 class="font-bold text-primary">{getPlayerName(player.user_id)}</h4>
                      <div class="badge badge-{player.state === 'ready' ? 'success' : 'warning'} badge-sm">
                        {player.state === 'ready' ? 'Ready' : 'Not Ready'}
                      </div>
                      {#if player.user_id === room.host}
                        <div class="badge badge-secondary badge-sm mt-1">Host</div>
                      {/if}
                    </div>
                  </div>
                {/each}

                <!-- Empty slots -->
                {#each Array(room.num_players - room.players.length) as _}
                  <div class="card bg-base-300/10 border-2 border-dashed border-primary/20">
                    <div class="card-body p-4 text-center">
                      <div class="avatar mb-2">
                        <div class="w-16 h-16 rounded-full bg-base-300/20">
                          <div class="text-2xl text-primary/30 flex items-center justify-center h-full">+</div>
                        </div>
                      </div>
                      <h4 class="font-bold text-primary/30">Waiting...</h4>
                    </div>
                  </div>
                {/each}
              </div>

              <!-- Action Buttons -->
              <div class="flex flex-wrap justify-end gap-2 mt-6">
                <div class="tooltip" data-tip={copyLinkTooltip}>
                  <button class="btn btn-outline btn-primary" on:click={copyRoomLink}>
                    Share Room
                  </button>
                </div>
                <button class="btn btn-secondary" on:click={() => showSettingsModal = true}>
                  Settings
                </button>
                <button
                  class="btn btn-accent animate-glow"
                  on:click={toggleReady}
                >
                  Toggle Ready
                </button>
                <button
                  class="btn btn-primary animate-glow"
                  disabled={!room.can_start}
                >
                  Start Game
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Chat Area -->
        <div class="card bg-base-100/50 backdrop-blur shadow-xl border border-primary/20 h-[600px]">
          <div class="card-body p-4 flex flex-col">
            <h3 class="text-xl font-bold text-primary mb-4">Room Chat</h3>

            <div class="flex-1 overflow-y-auto space-y-4 mb-4">
              {#each messages as message}
                <div class="chat chat-{message.sender === 'You' ? 'end' : 'start'}">
                  <div class="chat-header text-xs opacity-50">
                    {message.sender} • {message.timestamp}
                  </div>
                  <div class="chat-bubble chat-bubble-primary">
                    {message.text}
                  </div>
                </div>
              {/each}
            </div>

            <div class="join w-full">
              <input
                type="text"
                placeholder="Type a message..."
                class="input input-bordered join-item w-full bg-base-300/30 border-primary/50 text-primary"
                bind:value={newMessage}
                on:keypress={e => e.key === 'Enter' && handleSendMessage()}
              />
              <button
                class="btn btn-primary join-item"
                on:click={handleSendMessage}
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>

<!-- Settings Modal -->
{#if showSettingsModal}
  <dialog class="modal modal-bottom sm:modal-middle" open>
    <div class="modal-box bg-base-300 border border-primary/20">
      <h3 class="font-bold text-2xl mb-4 text-primary">Game Settings</h3>
      <div class="space-y-4">
        <div class="form-control">
          <label class="label">
            <span class="label-text text-primary">Game Mode</span>
          </label>
          <select class="select select-bordered bg-base-300/50 border-primary/50 text-primary">
            <option>Classic</option>
            <option>Custom</option>
          </select>
        </div>

        <div class="form-control">
          <label class="label">
            <span class="label-text text-primary">Role Configuration</span>
          </label>
          {#if room.game_config?.roles}
            {#each Object.entries(room.game_config.roles) as [role, count]}
              <div class="flex items-center gap-2 mb-2">
                <span class="capitalize">{role}:</span>
                <input
                  type="number"
                  min="0"
                  max="10"
                  value={count}
                  class="input input-bordered w-20 bg-base-300/50 border-primary/50 text-primary"
                />
              </div>
            {/each}
          {/if}
        </div>
      </div>
      <div class="modal-action">
        <button
          class="btn btn-ghost text-primary"
          on:click={() => showSettingsModal = false}
        >
          Cancel
        </button>
        <button class="btn btn-primary animate-glow">Save Changes</button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop bg-base-300/80">
      <button on:click={() => showSettingsModal = false}>close</button>
    </form>
  </dialog>
{/if}

<style>
  .chat-bubble {
    word-break: break-word;
    max-width: 80%;
  }

  .animate-glow {
    position: relative;
    overflow: hidden;
  }

  .animate-glow::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(
      45deg,
      transparent,
      rgba(45, 156, 219, 0.1),
      transparent
    );
    transform: rotate(45deg);
    animation: glow-sweep 3s linear infinite;
  }

  @keyframes glow-sweep {
    0% {
      transform: translate(-50%, -50%) rotate(45deg);
    }
    100% {
      transform: translate(50%, 50%) rotate(45deg);
    }
  }
</style>