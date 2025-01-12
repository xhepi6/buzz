<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { userStore } from '$lib/stores/userStore';

  let user = null;

  userStore.subscribe(value => {
    user = value;
  });

  onMount(() => {
    if (!user) {
      goto('/');
    }
  });
</script>

{#if user}
  <slot />
{/if} 