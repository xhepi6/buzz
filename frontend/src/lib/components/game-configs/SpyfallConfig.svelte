<script>
  export let config;
</script>

<ul class="space-y-1">
  <li class="text-cyber-secondary">
    Spies: {config.spyCount || 1}
  </li>
  <li class="text-cyber-secondary">
    Round Duration: {config.roundMinutes || 8} minutes
  </li>
  {#if config.useCustomLocations}
    <li class="text-emerald-400">
      Custom Locations: {config.customLocations?.length || 0}
    </li>
  {/if}
</ul> 