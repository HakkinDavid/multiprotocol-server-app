<script>
    import { onMount } from 'svelte';
    let selectedFile;
    let uploadResponse = '';
    let files = [];
  
    async function uploadFile() {
      const formData = new FormData();
      formData.append('file', selectedFile);
      const res = await fetch('http://localhost:8000/ftp/upload', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      uploadResponse = data.message;
      await loadFiles();
    }
  
    async function loadFiles() {
      const res = await fetch('http://localhost:8000/ftp/list');
      const data = await res.json();
      files = data.files;
    }
  
    onMount(loadFiles);
  </script>
  
  <h1>FTP File Management</h1>
  
  <h2>Upload File</h2>
  <input type="file" on:change="{e => selectedFile = e.target.files[0]}" />
  <button on:click={uploadFile}>Upload</button>
  <p>{uploadResponse}</p>
  
  <h2>Uploaded Files</h2>
  <ul>
    {#each files as file}
      <li>{file}</li>
    {/each}
  </ul>
  