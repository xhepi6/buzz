<!-- frontend/src/lib/components/AuthModal.svelte -->
<script>
  import Modal from './Modal.svelte';
  import { createEventDispatcher } from 'svelte';
  import { api } from '../api';
  import { userStore } from '../stores/userStore';

  const dispatch = createEventDispatcher();

  export let isOpen = false;
  export let message = '';
  
  let isLogin = true;
  let email = '';
  let password = '';
  let fullName = '';
  let nickname = '';
  let error = '';
  let isLoading = false;

  function resetForm() {
    email = '';
    password = '';
    fullName = '';
    nickname = '';
    error = '';
    isLoading = false;
  }

  function onClose() {
    resetForm();
    dispatch('close');
  }

  async function handleSubmit() {
    error = '';
    isLoading = true;
    
    try {
      if (isLogin) {
        await api.login(email, password);
      } else {
        await api.register(email, password, fullName, nickname);
      }
      
      // Get user profile and update store
      const user = await api.getCurrentUser();
      userStore.set(user);
      
      onClose();
    } catch (err) {
      error = err.message;
    } finally {
      isLoading = false;
    }
  }

  function switchMode() {
    isLogin = !isLogin;
    resetForm();
  }

  function handleSocialLogin(provider) {
    error = `${provider} login is not available yet`;
  }
</script>

<Modal {isOpen} {onClose} title={isLogin ? 'Login' : 'Sign Up'}>
  <form class="space-y-4" on:submit|preventDefault={handleSubmit}>
    {#if message}
      <div class="alert alert-info shadow-lg">
        <span>{message}</span>
      </div>
    {/if}

    {#if error}
      <div class="alert alert-error shadow-lg">
        <span>{error}</span>
      </div>
    {/if}

    {#if !isLogin}
      <div class="form-control w-full">
        <label class="label" for="fullName">
          <span class="label-text">Full Name</span>
        </label>
        <input
          id="fullName"
          type="text"
          placeholder="Enter your full name"
          class="input input-bordered w-full"
          bind:value={fullName}
          required
        />
      </div>

      <div class="form-control w-full">
        <label class="label" for="nickname">
          <span class="label-text">Nickname</span>
        </label>
        <input
          id="nickname"
          type="text"
          placeholder="Choose a nickname"
          class="input input-bordered w-full"
          bind:value={nickname}
          required
        />
      </div>
    {/if}
    
    <div class="form-control w-full">
      <label class="label" for="email">
        <span class="label-text">Email</span>
      </label>
      <input
        id="email"
        type="email"
        placeholder="Enter your email"
        class="input input-bordered w-full"
        bind:value={email}
        required
      />
    </div>
    
    <div class="form-control w-full">
      <label class="label" for="password">
        <span class="label-text">Password</span>
      </label>
      <input
        id="password"
        type="password"
        placeholder="Enter your password"
        class="input input-bordered w-full"
        bind:value={password}
        required
      />
    </div>

    <button 
      type="submit" 
      class="btn btn-primary w-full mt-6" 
      disabled={isLoading}
    >
      {#if isLoading}
        <span class="loading loading-spinner loading-sm"></span>
        Loading...
      {:else}
        {isLogin ? 'Login' : 'Sign Up'}
      {/if}
    </button>

    <div class="divider text-xs text-base-content/50">OR</div>

    <div class="space-y-3">
      <button
        type="button"
        class="btn btn-outline w-full opacity-50 cursor-not-allowed"
        disabled
        on:click={() => handleSocialLogin('Google')}
      >
        <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
          <path fill="currentColor" d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z"/>
        </svg>
        Continue with Google
      </button>
      
      <button
        type="button"
        class="btn btn-outline w-full opacity-50 cursor-not-allowed"
        disabled
        on:click={() => handleSocialLogin('Facebook')}
      >
        <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
          <path fill="currentColor" d="M12 2.04C6.5 2.04 2 6.53 2 12.06C2 17.06 5.66 21.21 10.44 21.96V14.96H7.9V12.06H10.44V9.85C10.44 7.34 11.93 5.96 14.22 5.96C15.31 5.96 16.45 6.15 16.45 6.15V8.62H15.19C13.95 8.62 13.56 9.39 13.56 10.18V12.06H16.34L15.89 14.96H13.56V21.96A10 10 0 0 0 22 12.06C22 6.53 17.5 2.04 12 2.04Z"/>
        </svg>
        Continue with Facebook
      </button>
    </div>

    <p class="text-center text-sm mt-4">
      {isLogin ? "Don't have an account?" : "Already have an account?"}
      <button
        type="button"
        class="text-primary hover:underline ml-1"
        on:click={switchMode}
      >
        {isLogin ? 'Sign Up' : 'Login'}
      </button>
    </p>
  </form>
</Modal>
