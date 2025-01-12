<script>
  import { onMount } from 'svelte';
  import AuthModal from './AuthModal.svelte';
  import { userStore } from '../stores/userStore';
  import { api } from '$lib/api';

  let showAuthModal = false;
  let user = null;

  userStore.subscribe(value => {
    user = value;
  });

  onMount(async () => {
    await userStore.initialize();
  });

  async function handleLogout() {
    api.logout();
    userStore.clearUser();
    window.location.href = '/';
  }

  function handleKeyDown(event) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      event.target.click();
    }
  }
</script>

<div class="navbar bg-base-100/50 backdrop-blur fixed top-0 z-50">
  <div class="flex-1">
    <a href="/" class="btn btn-ghost text-xl">
      <span class="text-primary">Buzz<span class="text-secondary">!</span></span>
    </a>
  </div>

  <div class="flex-none gap-2">
    {#if user}
      <div class="dropdown dropdown-end">
        <button 
          type="button"
          class="btn btn-ghost"
          aria-haspopup="menu"
          aria-expanded="false"
        >
          <div class="flex items-center space-x-2">
            <span class="hidden md:inline">{user.nickname}</span>
            <div class="avatar placeholder">
              <div class="bg-neutral text-neutral-content rounded-full w-8">
                <span class="text-xs" aria-hidden="true">{user.nickname.charAt(0).toUpperCase()}</span>
              </div>
            </div>
          </div>
        </button>
        <div 
          role="menu" 
          class="mt-3 p-2 shadow menu menu-compact dropdown-content bg-base-100 rounded-box w-52"
        >
          <a 
            href="/profile" 
            role="menuitem" 
            class="block px-4 py-2 hover:bg-base-200 rounded"
          >
            Profile
          </a>
          <button 
            type="button"
            role="menuitem"
            class="block w-full text-left px-4 py-2 hover:bg-base-200 rounded"
            on:click={handleLogout}
          >
            Logout
          </button>
        </div>
      </div>
    {:else}
      <button
        type="button"
        class="btn btn-primary btn-sm"
        on:click={() => showAuthModal = true}
      >
        Login
      </button>
    {/if}
  </div>
</div>

<AuthModal
  isOpen={showAuthModal}
  on:close={() => showAuthModal = false}
/>
