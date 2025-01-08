<!-- frontend/src/routes/profile/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { userStore } from '$lib/stores/userStore';

  let user;
  let isEditing = false;
  let error = '';
  let success = '';
  let isLoading = false;

  // Form data
  let formData = {
    full_name: '',
    nickname: '',
    password: '',
    confirm_password: ''
  };

  // Subscribe to user store
  userStore.subscribe(value => {
    user = value;
    if (user) {
      formData.full_name = user.full_name;
      formData.nickname = user.nickname;
    }
  });

  async function handleSubmit() {
    error = '';
    success = '';
    isLoading = true;

    try {
      // Validate passwords if being updated
      if (formData.password) {
        if (formData.password !== formData.confirm_password) {
          throw new Error('Passwords do not match');
        }
        if (formData.password.length < 6) {
          throw new Error('Password must be at least 6 characters');
        }
      }

      // Prepare update data
      const updateData = {
        full_name: formData.full_name,
        nickname: formData.nickname,
        ...(formData.password && { password: formData.password })
      };

      await userStore.updateProfile(updateData);
      success = 'Profile updated successfully';
      isEditing = false;
      formData.password = '';
      formData.confirm_password = '';
    } catch (err) {
      error = err.message;
    } finally {
      isLoading = false;
    }
  }
</script>

<!-- Add mt-16 to account for fixed navbar height -->
<div class="min-h-screen pt-20 pb-8 px-4">
  <div class="max-w-2xl mx-auto">
    <div class="mb-8 flex items-center">
      <h1 class="text-3xl font-bold">Profile</h1>
    </div>

    {#if !user}
      <div class="alert alert-warning">
        Please log in to view your profile.
      </div>
    {:else}
      {#if error}
        <div class="alert alert-error mb-4">
          <span>{error}</span>
        </div>
      {/if}

      {#if success}
        <div class="alert alert-success mb-4">
          <span>{success}</span>
        </div>
      {/if}

      <div class="card bg-base-200 shadow-xl">
        <div class="card-body">
          {#if !isEditing}
            <div class="space-y-4">
              <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label class="text-sm font-semibold text-base-content/70">Full Name</label>
                  <p class="text-lg">{user.full_name}</p>
                </div>
                
                <div>
                  <label class="text-sm font-semibold text-base-content/70">Nickname</label>
                  <p class="text-lg">{user.nickname}</p>
                </div>
                
                <div>
                  <label class="text-sm font-semibold text-base-content/70">Email</label>
                  <p class="text-lg">{user.email}</p>
                </div>
              </div>

              <div class="pt-4">
                <button 
                  class="btn btn-primary" 
                  on:click={() => isEditing = true}
                >
                  Edit Profile
                </button>
              </div>
            </div>
          {:else}
            <form on:submit|preventDefault={handleSubmit} class="space-y-4">
              <div class="form-control">
                <label class="label" for="full_name">
                  <span class="label-text">Full Name</span>
                </label>
                <input
                  id="full_name"
                  type="text"
                  class="input input-bordered w-full"
                  bind:value={formData.full_name}
                  required
                />
              </div>

              <div class="form-control">
                <label class="label" for="nickname">
                  <span class="label-text">Nickname</span>
                </label>
                <input
                  id="nickname"
                  type="text"
                  class="input input-bordered w-full"
                  bind:value={formData.nickname}
                  required
                />
              </div>

              <div class="form-control">
                <label class="label" for="password">
                  <span class="label-text">New Password (optional)</span>
                </label>
                <input
                  id="password"
                  type="password"
                  class="input input-bordered w-full"
                  bind:value={formData.password}
                />
              </div>

              {#if formData.password}
                <div class="form-control">
                  <label class="label" for="confirm_password">
                    <span class="label-text">Confirm New Password</span>
                  </label>
                  <input
                    id="confirm_password"
                    type="password"
                    class="input input-bordered w-full"
                    bind:value={formData.confirm_password}
                    required={!!formData.password}
                  />
                </div>
              {/if}

              <div class="flex gap-4 pt-4">
                <button 
                  type="submit" 
                  class="btn btn-primary"
                  disabled={isLoading}
                >
                  {#if isLoading}
                    <span class="loading loading-spinner loading-sm"></span>
                    Saving...
                  {:else}
                    Save Changes
                  {/if}
                </button>
                <button 
                  type="button" 
                  class="btn btn-ghost"
                  on:click={() => {
                    isEditing = false;
                    error = '';
                    formData.password = '';
                    formData.confirm_password = '';
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          {/if}
        </div>
      </div>
    {/if}
  </div>
</div>
