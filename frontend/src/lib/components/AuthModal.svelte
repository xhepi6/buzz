<script>
  import Modal from './Modal.svelte';
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  export let isOpen = false;

  let isLogin = true;
  let email = '';
  let password = '';
  let name = '';

  function onClose() {
    dispatch('close');
  }

  async function handleSubmit() {
    // TODO: Implement authentication logic
    console.log(isLogin ? 'Login' : 'Sign up', { email, password, name });
  }

  function handleSocialLogin(provider) {
    // TODO: Implement social login
    console.log(`Login with ${provider}`);
  }
</script>

<Modal {isOpen} onClose={onClose} title={isLogin ? 'Login' : 'Sign Up'}>
  <form class="space-y-4" on:submit|preventDefault={handleSubmit}>
    {#if !isLogin}
      <div class="form-control">
        <input
          type="text"
          placeholder="Name"
          class="input input-bordered bg-cyber-bg/50 border-cyber-primary/50"
          bind:value={name}
          required
        />
      </div>
    {/if}

    <div class="form-control">
      <input
        type="email"
        placeholder="Email"
        class="input input-bordered bg-cyber-bg/50 border-cyber-primary/50"
        bind:value={email}
        required
      />
    </div>

    <div class="form-control">
      <input
        type="password"
        placeholder="Password"
        class="input input-bordered bg-cyber-bg/50 border-cyber-primary/50"
        bind:value={password}
        required
      />
    </div>

    <button type="submit" class="btn btn-primary w-full">
      {isLogin ? 'Login' : 'Sign Up'}
    </button>

    <div class="divider text-cyber-primary/50">OR</div>

    <div class="space-y-2">
      <button
        type="button"
        class="btn btn-outline w-full"
        on:click={() => handleSocialLogin('google')}
      >
        <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
          <path fill="currentColor" d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z"/>
        </svg>
        Continue with Google
      </button>

      <button
        type="button"
        class="btn btn-outline w-full"
        on:click={() => handleSocialLogin('facebook')}
      >
        <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
          <path fill="currentColor" d="M12 2.04C6.5 2.04 2 6.53 2 12.06C2 17.06 5.66 21.21 10.44 21.96V14.96H7.9V12.06H10.44V9.85C10.44 7.34 11.93 5.96 14.22 5.96C15.31 5.96 16.45 6.15 16.45 6.15V8.62H15.19C13.95 8.62 13.56 9.39 13.56 10.18V12.06H16.34L15.89 14.96H13.56V21.96A10 10 0 0 0 22 12.06C22 6.53 17.5 2.04 12 2.04Z"/>
        </svg>
        Continue with Facebook
      </button>
    </div>

    <p class="text-center text-sm">
      {isLogin ? "Don't have an account?" : "Already have an account?"}
      <button
        type="button"
        class="text-cyber-primary hover:underline"
        on:click={() => isLogin = !isLogin}
      >
        {isLogin ? 'Sign Up' : 'Login'}
      </button>
    </p>
  </form>
</Modal>
