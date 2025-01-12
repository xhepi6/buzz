<script>
  export let role;
  export let description;
  export let teammates = [];

  // Role-specific styling
  $: cardStyle = {
    mafia: 'bg-red-900/50 border-red-500',
    civilian: 'bg-blue-900/50 border-blue-500',
    doctor: 'bg-green-900/50 border-green-500',
    police: 'bg-yellow-900/50 border-yellow-500'
  }[role.toLowerCase()] || 'bg-base-200/50 border-cyber-primary';

  $: textStyle = {
    mafia: 'text-red-400',
    civilian: 'text-blue-400',
    doctor: 'text-green-400',
    police: 'text-yellow-400'
  }[role.toLowerCase()] || 'text-cyber-primary';
</script>

<div class="card w-full {cardStyle} border-2 backdrop-blur shadow-xl transform hover:scale-105 transition-transform duration-300">
  <div class="card-body">
    <h2 class="card-title text-3xl font-bold mb-4 {textStyle}">
      {role}
    </h2>
    
    <p class="text-cyber-primary/80 mb-6">
      {description}
    </p>

    {#if teammates && teammates.length > 0}
      <div class="border-t border-cyber-primary/20 pt-4">
        <h3 class="text-lg font-semibold mb-2 {textStyle}">Your Team:</h3>
        <ul class="space-y-2">
          {#each teammates as teammate}
            <li class="text-cyber-primary/70">{teammate.nickname}</li>
          {/each}
        </ul>
      </div>
    {/if}
  </div>
</div> 