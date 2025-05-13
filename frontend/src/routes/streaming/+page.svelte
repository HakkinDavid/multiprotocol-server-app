<script>
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { onMount } from 'svelte';

  let files = [];
  let selected = '';
  let type = '';

  async function fetchFiles() {
    const res = await fetch('/api/streaming/list');
    const data = await res.json();
    files = data.files;
  }

  function play(file) {
    selected = file;
    const ext = file.split('.').pop().toLowerCase();
    if (['mp3', 'ogg', 'wav'].includes(ext)) type = 'audio';
    else if (['mp4', 'webm'].includes(ext)) type = 'video';
    else type = '';
  }

  onMount(fetchFiles);
</script>

<Header title="Streaming 📺" />

<main class="container mx-auto px-4 py-8 min-h-[calc(100vh-200px)]">
  <h2 class="text-2xl font-semibold text-gray-800 mb-4">Archivos disponibles para streaming</h2>

  <div class="bg-gray-50 border rounded-lg p-4 mb-6 max-h-[300px] overflow-y-auto">
    {#if files.length > 0}
      <ul class="space-y-2">
        {#each files as file}
          <li class="flex justify-between items-center">
            <span>{file}</span>
            <button
              on:click={() => play(file)}
              class="bg-red-500 hover:bg-red-600 text-white text-sm px-3 py-1 rounded-full"
            >
              Reproducir
            </button>
          </li>
        {/each}
      </ul>
    {:else}
      <p class="text-gray-500">No hay archivos disponibles.</p>
    {/if}
  </div>

  {#if selected && type === 'video'}
    <div class="mb-6">
      <h3 class="text-lg font-semibold mb-2">Reproduciendo video: {selected}</h3>
      <video class="w-full rounded-lg shadow" controls>
        <source src={`/api/streaming/play/${selected}`} type="video/mp4" />
        Tu navegador no soporta video.
      </video>
    </div>
  {/if}

  {#if selected && type === 'audio'}
    <div class="mb-6">
      <h3 class="text-lg font-semibold mb-2">Reproduciendo audio: {selected}</h3>
      <audio class="w-full" controls>
        <source src={`/api/streaming/play/${selected}`} type="audio/mpeg" />
        Tu navegador no soporta audio.
      </audio>
    </div>
  {/if}
</main>

<Footer />
