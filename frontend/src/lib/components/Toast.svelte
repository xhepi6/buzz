<script>
  import { toastStore } from '$lib/stores/toastStore';
  import { fly } from 'svelte/transition';
</script>

<div class="toast toast-top toast-center z-50">
  {#each $toastStore as toast (toast.id)}
    <div
      transition:fly={{ y: -30, duration: 300 }}
      class="alert {toast.type === 'error' ? 'alert-error' : 
             toast.type === 'success' ? 'alert-success' : 
             toast.type === 'warning' ? 'alert-warning' : 
             'alert-info'}"
    >
      <span>{toast.message}</span>
    </div>
  {/each}
</div> 