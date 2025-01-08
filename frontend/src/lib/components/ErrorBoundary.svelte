<script>
    let error = null;

    function handleError(event) {
      error = event.error;
    }
  </script>

  <svelte:window on:error={handleError} />

  {#if error}
    <div class="alert alert-error">
      <h3>Something went wrong</h3>
      <p>{error.message}</p>
      <button class="btn btn-primary" on:click={() => window.location.reload()}>
        Reload Page
      </button>
    </div>
  {:else}
    <slot />
  {/if}
