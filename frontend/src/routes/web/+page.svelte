<script>
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { onMount } from 'svelte';
  import { PUBLIC_BACKEND_URL } from '$env/static/public';
  let content = '';

  async function loadContent() {
    const res = await fetch(`${PUBLIC_BACKEND_URL}/web/content`);
    const data = await res.json();
    content = data.content;
  }

  onMount(loadContent);
</script>

<Header title="Web 🌐" />

<main class="container mx-auto px-4 py-8 w-full h-full">
  <h2 class="text-2xl font-semibold text-gray-800 mb-4">Static HTML webview</h2>
  <!-- svelte-ignore a11y_missing_attribute -->
  <iframe srcdoc={content} class="rounded border overflow-hidden shadow-md w-full min-h-[calc(100vh-200px)] h-full"></iframe>
</main>

<Footer />