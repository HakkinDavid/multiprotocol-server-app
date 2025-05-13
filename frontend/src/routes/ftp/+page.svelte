<script>
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { onMount } from 'svelte';

  let files = [];
  let fileToUpload = null;
  let message = '';

  async function fetchFiles() {
    const res = await fetch('/api/ftp/list');
    const data = await res.json();
    files = data.files;
  }

  async function upload() {
    if (!fileToUpload) {
      message = 'Selecciona un archivo para subir';
      return;
    }

    const formData = new FormData();
    formData.append('file', fileToUpload);

    const res = await fetch('/api/ftp/upload', {
      method: 'POST',
      body: formData
    });

    const result = await res.json();
    message = result.message || 'Archivo subido';
    fileToUpload = null;
    await fetchFiles();
  }

  function download(file) {
    window.open(`/api/ftp/download/${file}`, '_blank');
  }

  onMount(fetchFiles);
</script>

<Header title="FTP 📁" />

<main class="container mx-auto px-4 py-8 min-h-[calc(100vh-200px)]">
  <h2 class="text-2xl font-semibold text-gray-800 mb-4">Subida y descarga de archivos</h2>

  <div class="bg-white rounded-lg p-4 shadow mb-6">
    <label class="block text-sm text-gray-700 mb-2">Selecciona archivo para subir:</label>
    <input type="file" on:change={(e) => fileToUpload = e.target.files[0]} class="mb-2" />
    <button on:click={upload} class="bg-purple-500 hover:bg-purple-600 text-white px-4 py-1 rounded-full text-sm">
      Subir archivo
    </button>
    {#if message}
      <p class="text-sm text-gray-600 mt-2">{message}</p>
    {/if}
  </div>

  <div class="bg-gray-50 border rounded-lg p-4 max-h-[300px] overflow-y-auto">
    <h3 class="text-lg font-semibold mb-2">Archivos disponibles</h3>
    {#if files.length > 0}
      <ul class="space-y-2">
        {#each files as file}
          <li class="flex justify-between items-center">
            <span>{file}</span>
            <button
              on:click={() => download(file)}
              class="bg-gray-200 hover:bg-gray-300 text-sm px-3 py-1 rounded-full"
            >
              Descargar
            </button>
          </li>
        {/each}
      </ul>
    {:else}
      <p class="text-gray-500">No hay archivos disponibles.</p>
    {/if}
  </div>
</main>

<Footer />
