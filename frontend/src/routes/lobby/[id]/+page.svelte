<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { api } from '$lib/api';

  const API_URL = import.meta.env.VITE_API_URL;

  let game = null;
  let messages = [];
  let newMessage = '';
  let showSettingsModal = false;
  let copyLinkTooltip = 'Copy Link';
  let loading = true;
  let error = null;

  let players = [
    { id: 1, name: "CyberRunner", ready: true, avatar: "/api/placeholder/100/100" },
    { id: 2, name: "NeonBlade", ready: false, avatar: "/api/placeholder/100/100" },
    { id: 3, name: "DataPunk", ready: false, avatar: "/api/placeholder/100/100" }
  ];

  async function loadGameDetails() {
    try {
      const gameId = $page.params.id;
      game = await api.getGameDetails(gameId);
    } catch (err) {
      error = err.message;
    } finally {
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

  function handleReady() {
    const currentPlayer = players.find(p => p.id === 1);
    if (currentPlayer) {
      currentPlayer.ready = !currentPlayer.ready;
      players = [...players];
    }
  }

  onMount(() => {
    loadGameDetails();
  });
</script>

<title>Buzz! - Lobby</title>

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
  {:else if game}
    <div class="container mx-auto p-4">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Main Game Area -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Room Info -->
          <div class="card bg-base-100/50 backdrop-blur shadow-xl border border-primary/20">
            <div class="card-body">
              <div class="flex justify-between items-center">
                <div>
                  <h2 class="card-title text-2xl text-primary">Cyber Room #1337</h2>
                  <div class="badge badge-secondary mt-2">{game.name}</div>
                </div>
                <img 
                  src={`${API_URL}${game.image_url}`}
                  alt={game.name}
                  class="w-32 h-32 object-cover rounded-lg border border-primary/20" 
                />
              </div>
              
              <!-- Game Status -->
              <div class="mt-4 flex flex-wrap gap-4">
                <div class="stat bg-base-300/30 rounded-box p-4 flex-1">
                  <div class="stat-title text-primary/70">Players</div>
                  <div class="stat-value text-primary">{players.length}/{game.max_players}</div>
                </div>
                <div class="stat bg-base-300/30 rounded-box p-4 flex-1">
                  <div class="stat-title text-primary/70">Duration</div>
                  <div class="stat-value text-accent">{game.duration_minutes}min</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Players Grid -->
          <div class="card bg-base-100/50 backdrop-blur shadow-xl border border-primary/20">
            <div class="card-body">
              <h3 class="text-xl font-bold text-primary mb-4">Players</h3>
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {#each players as player}
                  <div class="card bg-base-300/30 hover:bg-base-300/40 transition-all">
                    <div class="card-body p-4 text-center">
                      <div class="avatar mb-2">
                        <div class="w-16 h-16 rounded-full ring ring-primary/30 ring-offset-base-100 ring-offset-2">
                          <img src={player.avatar} alt={player.name} />
                        </div>
                      </div>
                      <h4 class="font-bold text-primary">{player.name}</h4>
                      <div class="badge badge-{player.ready ? 'success' : 'warning'} badge-sm">
                        {player.ready ? 'Ready' : 'Not Ready'}
                      </div>
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
                  on:click={handleReady}
                >
                  Toggle Ready
                </button>
                <button 
                  class="btn btn-primary animate-glow" 
                  disabled={!players.every(p => p.ready)}
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
            <option>Time Attack</option>
            <option>Custom</option>
          </select>
        </div>
        
        <div class="form-control">
          <label class="label">
            <span class="label-text text-primary">Round Time (minutes)</span>
          </label>
          <input 
            type="number" 
            min="1" 
            max="10" 
            value="3"
            class="input input-bordered bg-base-300/50 border-primary/50 text-primary"
          />
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