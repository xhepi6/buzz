<script>
  export let config;
</script>

<ul class="space-y-1">
  <li class="text-cyber-secondary">
    Mafia: {config.roles?.mafia || 0}
  </li>
  <li class="text-cyber-secondary">
    Civilians: {config.roles?.civilian || 0}
  </li>
  {#if config.roles?.doctor > 0}
    <li class="text-emerald-400">
      Doctor: {config.roles.doctor}
    </li>
  {/if}
  {#if config.roles?.police > 0}
    <li class="text-emerald-400">
      Police: {config.roles.police}
    </li>
  {/if}
  {#if config.roles?.moderator}
    <li class="text-emerald-400">
      Moderator: {config.roles.moderator ? 'Yes' : 'No'}
    </li>
  {/if}
</ul> 