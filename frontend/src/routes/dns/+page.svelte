<script>
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  let ip = '';
  let timestamp = '';
  let records = [];
  let error = '';

  async function registerIP() {
    error = '';
    try {
      const res = await fetch('/api/dns/register', { method: 'POST' });
      if (!res.ok) throw new Error('No se pudo registrar la IP');
      const data = await res.json();
      ip = data.ip;
      timestamp = data.timestamp;
      await fetchRecords();
    } catch (err) {
      error = err.message;
    }
  }

  async function fetchRecords() {
    const res = await fetch('/api/dns/records');
    const data = await res.json();
    records = data.records;
  }

  onMount(fetchRecords);
</script>

<Header title="Servicio DNS 🌐" />

<main class="container mx-auto px-4 py-8 min-h-[calc(100vh-200px)]">
  <div class="mb-6">
    <h2 class="text-2xl font-semibold text-gray-800 mb-2">Registro de IPs</h2>
    <p class="text-gray-600">Haz clic para registrar tu IP actual</p>
  </div>

  <button
    on:click={registerIP}
    class="bg-cyan-500 hover:bg-cyan-600 text-white px-6 py-2 rounded-full mb-4"
  >
    Registrar mi IP
  </button>

  {#if ip}
    <div class="mb-4 text-green-700 bg-green-100 p-3 rounded-lg">
      IP registrada: <strong>{ip}</strong> a las <strong>{timestamp}</strong>
    </div>
  {/if}

  {#if error}
    <div class="mb-4 text-red-700 bg-red-100 p-3 rounded-lg">
      {error}
    </div>
  {/if}

  <h3 class="text-lg font-semibold mt-6 mb-2">Historial de registros:</h3>
  <div class="bg-gray-50 border rounded-lg p-4 max-h-[300px] overflow-auto">
    {#if records.length > 0}
      <ul class="text-sm text-gray-700 space-y-1">
        {#each records as line}
          <li>{line}</li>
        {/each}
      </ul>
    {:else}
      <p class="text-gray-500">No hay registros aún.</p>
    {/else}
  </div>
</main>

<Footer />
