<script>
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import LiveStream from '$lib/components/LiveStream.svelte';
  import { PUBLIC_BACKEND_URL, PUBLIC_WS_URL } from '$env/static/public';
  import { onMount, onDestroy } from 'svelte';

  let files = [];
  let selected = null;
  let type = '';
  let fileToUpload;
  let uploading = false;
  let uploadProgress = 0;
  let errorMessage = '';
  let successMessage = '';
  let video_element;
  let audio_element;

  async function fetchFiles() {
    try {
      const res = await fetch(`${PUBLIC_BACKEND_URL}/streaming/list`);
      const data = await res.json();
      files = data.files || [];
      errorMessage = '';
    } catch (err) {
      console.error('Error al cargar archivos:', err);
      errorMessage = 'Error al cargar la lista de archivos';
    }
  }

  function play(file) {
    const ext = file.split('.').pop().toLowerCase();
    switch (ext) {
      case 'mp3':
      case 'ogg':
      case 'wav':
      case 'aac':
      case 'flac':
        type = 'audio';
        break;
      case 'mp4':
      case 'webm':
      case 'avi':
      case 'mov':
      case 'mkv':
        type = 'video';
        break;
      case 'txt':
        type = 'text';
        break;
      case 'png':
      case 'jpeg':
      case 'jpg':
      case 'svg':
      case 'gif':
        type = 'image';
        break;
      default:
        type = '';
        break;
    }

    if (selected) {
      selected = file;
      if (video_element && type === 'video') video_element.load();
      else if (audio_element && type === 'audio') audio_element.load();
    }
    else {
      selected = file;
    }
  }

  async function uploadFile() {
    if (!fileToUpload) {
      errorMessage = 'Por favor selecciona un archivo';
      return;
    }

    const formData = new FormData();
    formData.append('file', fileToUpload);
    
    try {
      uploading = true;
      errorMessage = '';
      successMessage = '';
      
      const xhr = new XMLHttpRequest();
      
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          uploadProgress = Math.round((event.loaded / event.total) * 100);
        }
      });
      
      xhr.onload = async () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          successMessage = 'Archivo subido correctamente';
          fileToUpload = null;
          uploadProgress = 0;
          await fetchFiles();
        } else {
          errorMessage = `Error al subir: ${xhr.statusText}`;
        }
        uploading = false;
      };
      
      xhr.onerror = () => {
        errorMessage = 'Error de red al subir el archivo';
        uploading = false;
      };
      
      xhr.open('POST', `${PUBLIC_BACKEND_URL}/streaming/upload`);
      xhr.send(formData);
      
    } catch (err) {
      console.error('Error:', err);
      errorMessage = 'Error al subir el archivo';
      uploading = false;
    }
  }

  onMount(fetchFiles);
  
</script>

<Header title="Streaming 📺" />

<main class="container mx-auto px-4 py-8 min-h-[calc(100vh-200px)]">
  <!-- Mensajes de error/éxito -->
  {#if errorMessage}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 mb-4 rounded" role="alert">
      <span class="block sm:inline">{errorMessage}</span>
    </div>
  {/if}
  
  {#if successMessage}
    <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 mb-4 rounded" role="alert">
      <span class="block sm:inline">{successMessage}</span>
    </div>
  {/if}

  <!-- Sección de carga de archivos -->
  <div class="bg-white shadow-md rounded p-6 mb-6">
    <h2 class="text-xl font-semibold text-gray-800 mb-4">Subir nuevo contenido</h2>
    
    <div class="flex items-center space-x-4">
      <input 
        type="file" 
        id="file-upload" 
        class="hidden" 
        accept="video/*,audio/*"
        on:change={(e) => fileToUpload = e.target.files[0]}
      />
      <label 
        for="file-upload"
        class="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded cursor-pointer"
      >
        Seleccionar archivo
      </label>
      <span class="text-gray-600">{fileToUpload ? fileToUpload.name : 'Ningún archivo seleccionado'}</span>
      
      <button 
        on:click={uploadFile}
        disabled={!fileToUpload || uploading}
        class="bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded disabled:opacity-50"
      >
        {uploading ? 'Subiendo...' : 'Subir'}
      </button>
    </div>
    
    {#if uploading}
      <div class="mt-4">
        <div class="bg-gray-200 rounded-full h-2.5 mt-2">
          <div class="bg-blue-600 h-2.5 rounded-full" style="width: {uploadProgress}%"></div>
        </div>
        <span class="text-sm text-gray-600">{uploadProgress}%</span>
      </div>
    {/if}
  </div>

  <LiveStream/>

  <!-- Sección de contenido para streaming -->
  <h2 class="text-2xl font-semibold text-gray-800 mb-4">Archivos disponibles para streaming</h2>

  <div class="bg-gray-50 border rounded-lg p-4 mb-6 max-h-[300px] overflow-y-auto">
    {#if files.length > 0}
      <ul class="space-y-2">
        {#each files as file}
          <li class="flex justify-between items-center p-2 hover:bg-gray-100 rounded">
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
      <video bind:this={video_element} class="w-full rounded-lg shadow" controls>
        <source src={`${PUBLIC_BACKEND_URL}/streaming/play/${selected}`} type="video/mp4" />
        Tu navegador no soporta video.
      </video>
    </div>
  {/if}

  {#if selected && type === 'audio'}
    <div class="mb-6">
      <h3 class="text-lg font-semibold mb-2">Reproduciendo audio: {selected}</h3>
      <audio bind:this={audio_element} class="w-full" controls>
        <source src={`${PUBLIC_BACKEND_URL}/streaming/play/${selected}`} type="audio/mpeg" />
        Tu navegador no soporta audio.
      </audio>
    </div>
  {/if}

  {#if selected && type === 'text'}
    {#await (async () => {
      let txt_req = await fetch(`${PUBLIC_BACKEND_URL}/streaming/play/${selected}`)
      let content = await (await txt_req.blob()).text()
      return content
    })()}
      Cargando...
    {:then text_file_stream}
      <div class="mb-6">
        <h3 class="text-lg font-semibold mb-2">Texto: {selected}</h3>
        <iframe class="w-full" srcdoc={text_file_stream} frameBorder="0">
        </iframe>
      </div>
    {/await}
  {/if}

  {#if selected && type === 'image'}
    <div class="mb-6">
      <h3 class="text-lg font-semibold mb-2">Imagen: {selected}</h3>
      <img src={`${PUBLIC_BACKEND_URL}/streaming/play/${selected}`} class="w-full rounded-lg shadow" />
    </div>
  {/if}
</main>

<Footer />

