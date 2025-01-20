<script>
  import { page } from '$app/stores';
  import { userStore } from '$lib/stores/userStore';
  import { browser } from '$app/environment';
  import AuthModal from './AuthModal.svelte';

  // Track loading state
  let isLoading = true;
  let showAuthModal = false;

  // Subscribe to user store to handle loading state
  userStore.subscribe(value => {
    if (browser) {
      // Only update loading state once we have a definitive user value
      isLoading = false;
    }
  });

  function handleKeyDown(event) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      event.target.click();
    }
  }
</script>

<div class="navbar bg-base-100/50 backdrop-blur fixed top-0 z-50 border-b border-cyber-primary/20">
  <div class="navbar-start">
    <a href="/" class="btn btn-ghost text-xl">
      <span class="text-cyber-primary">BUZZ!</span>
    </a>
  </div>
  
  <div class="navbar-end">
    {#if !isLoading}
      {#if $userStore}
        <div class="dropdown dropdown-end">
          <button type="button" class="btn btn-ghost">
            <div class="flex items-center space-x-2">
              <span class="text-cyber-accent">{$userStore.nickname}</span>
              <div class="avatar placeholder">
                <div class="bg-neutral text-neutral-content rounded-full w-8">
                  <span class="text-xs" aria-hidden="true">{$userStore.nickname.charAt(0).toUpperCase()}</span>
                </div>
              </div>
            </div>
          </button>
          <ul 
            tabindex="0" 
            class="menu dropdown-content z-[1] p-2 shadow bg-base-100 rounded-box w-52 mt-4"
            role="menu"
          >
            <li role="none">
              <a 
                href="/profile" 
                role="menuitem" 
                class="block px-4 py-2 hover:bg-base-200 rounded"
              >
                Profile
              </a>
            </li>
            <li role="none">
              <button 
                class="block w-full text-left px-4 py-2 hover:bg-base-200 rounded text-error" 
                role="menuitem"
                on:click={() => {
                  userStore.logout();
                  window.location.href = '/';
                }}
              >
                Logout
              </button>
            </li>
          </ul>
        </div>
      {:else}
        <button
          type="button"
          class="btn btn-primary"
          on:click={() => showAuthModal = true}
        >
          Login
        </button>
      {/if}
    {/if}
  </div>
</div>

<AuthModal
  isOpen={showAuthModal}
  on:close={() => showAuthModal = false}
/>
