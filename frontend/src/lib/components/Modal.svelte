<script>
  export let isOpen = false;
  export let onClose = () => {};
  export let title = '';

  function handleBackdropClick(event) {
    if (event.target === event.currentTarget) {
      onClose();
    }
  }
</script>

{#if isOpen}
  <div
    class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
    on:click={handleBackdropClick}
  >
    <div class="bg-base-100 rounded-lg w-full max-w-md relative border border-cyber-primary/30">
      <div class="p-6">
        {#if title}
          <h2 class="text-2xl font-bold mb-4 text-cyber-primary">{title}</h2>
        {/if}
        <button
          class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2"
          on:click={onClose}
        >
          ✕
        </button>
        <slot />
      </div>
    </div>
  </div>
{/if} 