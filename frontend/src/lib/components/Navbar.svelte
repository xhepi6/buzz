<script>
  import AuthModal from './AuthModal.svelte';

  let isDarkMode = true;
  let showAuthModal = false;

  function toggleTheme() {
    isDarkMode = !isDarkMode;
    document.documentElement.setAttribute('data-theme', isDarkMode ? 'cyberpunk' : 'light');
  }
</script>

<div class="navbar bg-base-100/50 backdrop-blur fixed top-0 z-50">
  <a href="/" class="btn btn-ghost text-xl">
    <span class="text-primary">Buzz<span class="text-secondary">!</span></span>
  </a>
  <div class="ml-auto">
    <button
      class="btn btn-primary btn-sm"
      on:click={() => showAuthModal = true}
    >
      Login
    </button>
  </div>
</div>

<AuthModal
  isOpen={showAuthModal}
  on:close={() => showAuthModal = false}
/>
