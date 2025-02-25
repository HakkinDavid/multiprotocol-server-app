<script>
    import { onMount } from 'svelte';
    let status = '';
    let message = '';
  
    async function loadStatus() {
      const res = await fetch('http://localhost:8000/streaming/status');
      const data = await res.json();
      status = data.status;
    }
  
    async function startStreaming() {
      const res = await fetch('http://localhost:8000/streaming/start', { method: 'POST' });
      const data = await res.json();
      message = data.message;
      loadStatus();
    }
  
    async function stopStreaming() {
      const res = await fetch('http://localhost:8000/streaming/stop', { method: 'POST' });
      const data = await res.json();
      message = data.message;
      loadStatus();
    }
  
    onMount(loadStatus);
  </script>
  
  <h1>Streaming Service</h1>
  <p>Current Status: {status}</p>
  <button on:click={startStreaming}>Start Streaming</button>
  <button on:click={stopStreaming}>Stop Streaming</button>
  <p>{message}</p>
  