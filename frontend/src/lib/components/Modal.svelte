<!-- frontend/src/lib/components/Modal.svelte -->
<script>
  import { createEventDispatcher, onMount } from 'svelte';
  const dispatch = createEventDispatcher();
  

  export let isOpen = false;
  export let title = '';
  export let onClose;

  let modalContent;

  function handleEscape(event) {
    if (event.key === 'Escape' && isOpen) {
      onClose();
    }
  }

  function handleOverlayClick(event) {
    if (event.target === event.currentTarget) {
      onClose();
    }
  }

  onMount(() => {
    document.addEventListener('keydown', handleEscape);
    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  });
</script>

{#if isOpen}
  <!-- Overlay -->
  <div
    class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4 overflow-y-auto"
    role="dialog"
    aria-labelledby="modal-title"
    aria-modal="true"
    on:click={handleOverlayClick}
  >
    <!-- Modal -->
    <div 
      class="bg-base-100 rounded-lg shadow-xl w-full max-w-md relative"
      role="document"
      bind:this={modalContent}
    >
      <!-- Close button -->
      <button
        type="button"
        class="absolute top-4 right-4 p-2 rounded-lg hover:bg-base-200 transition-colors"
        aria-label="Close modal"
        on:click={onClose}
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <!-- Content -->
      <div class="p-6">
        {#if title}
          <h2 id="modal-title" class="text-xl font-bold mb-6 pr-8">{title}</h2>
        {/if}
        <div class="mt-2">
          <slot></slot>
        </div>
      </div>
    </div>
  </div>
{/if}
