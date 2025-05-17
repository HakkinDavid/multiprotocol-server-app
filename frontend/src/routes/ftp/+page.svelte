<script>
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { onMount } from 'svelte';
  import { PUBLIC_BACKEND_URL } from '$env/static/public';

  let files = [];
  let fileToUpload = null;
  let message = '';
  let file_input;

  async function fetchFiles() {
    const res = await fetch(`${PUBLIC_BACKEND_URL}/ftp/list`);
    const data = await res.json();
    files = data.files;
  }

  async function upload() {
    if (!fileToUpload) {
      file_input.click();
      return;
    }

    const formData = new FormData();
    formData.append('file', fileToUpload);

    const res = await fetch(`${PUBLIC_BACKEND_URL}/ftp/upload`, {
      method: 'POST',
      body: formData
    });

    const result = await res.json();
    message = result.message || 'File has been uploaded';
    fileToUpload = null;
    await fetchFiles();
  }

  function download(file) {
    window.open(`${PUBLIC_BACKEND_URL}/ftp/download/${file}`, '_blank');
  }

  onMount(fetchFiles);
</script>

<Header title="FTP 📁" />

<main class="container mx-auto px-4 py-8 min-h-[calc(100vh-200px)]">
  <h2 class="text-2xl font-semibold text-gray-800 mb-4">File upload and download</h2>

  <div class="flex flex-row flex-wrap gap-2 bg-white rounded-lg p-4 shadow mb-6">
    <p class="border border-purple-500 rounded-lg w-1/2 px-4 place-content-center justify-center items-center text-center">{fileToUpload ? fileToUpload.name : "No file has been selected"}</p>
    <button on:click={upload} class:bg-purple-500={!fileToUpload} class:hover:bg-purple-600={!fileToUpload} class:bg-green-500={fileToUpload} class:hover:bg-green-600={fileToUpload} class="text-white px-4 py-1 rounded-full text-sm place-content-center justify-center items-center text-center w-32">
      {fileToUpload ? "Upload" : "Choose"}
    </button>
    {#if message}
      <p class="text-sm text-gray-600 place-content-center justify-center items-center text-center">{message}</p>
    {/if}
  </div>

  <div class="bg-gray-50 border rounded-lg p-4 max-h-[300px] overflow-y-auto">
    <h3 class="text-lg font-semibold mb-2">Available files</h3>
    {#if files.length > 0}
      <ul class="space-y-2">
        {#each files as file}
          <li class="flex justify-between items-center">
            <span>{file}</span>
            <button
              on:click={() => download(file)}
              class="bg-gray-200 hover:bg-gray-300 text-sm px-3 py-1 rounded-full"
            >
              Download
            </button>
          </li>
        {/each}
      </ul>
    {:else}
      <p class="text-gray-500">There are no files currently available...</p>
    {/if}
  </div>
</main>

<Footer />
<input bind:this={file_input} type="file" on:change={(e) => fileToUpload = e.target.files[0]} class="w-0 h-0"/>