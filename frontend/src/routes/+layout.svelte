<script>
  import "../app.css";
  import Navbar from "$lib/components/Navbar.svelte";
  import ErrorBoundary from "$lib/components/ErrorBoundary.svelte";
  import Toast from "$lib/components/Toast.svelte";
</script>

<ErrorBoundary>
  <main class="min-h-screen bg-base-300">
    <Navbar />
    <slot />
  </main>
</ErrorBoundary>

<Toast />
