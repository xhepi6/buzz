<script>
  import MafiaConfig from './game-configs/MafiaConfig.svelte';
  import SpyfallConfig from './game-configs/SpyfallConfig.svelte';

  export let gameType;
  export let config;

  const configComponents = {
    mafia: MafiaConfig,
    spyfall: SpyfallConfig
  };
</script>

<div class="card bg-base-100/50 backdrop-blur shadow-xl border border-cyber-primary/20 mb-6">
  <div class="p-6">
    <h2 class="text-lg font-bold text-cyber-primary mb-4">Game Configuration</h2>
    <svelte:component this={configComponents[gameType]} {config} />
  </div>
</div> 