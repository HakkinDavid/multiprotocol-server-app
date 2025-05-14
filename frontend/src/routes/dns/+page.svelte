<script>
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let ip = '';
	let timestamp = '';
	let records = [];
	let error = '';

	const backendUrl = 'http://localhost:8000'; // Hay que cambiar esto por un archivo config o variable de entorno

	async function registerIP() {
		error = '';
		try {
			const res = await fetch(`${backendUrl}/dns/register`, { method: 'POST' });
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

<main class="container mx-auto min-h-[calc(100vh-200px)] px-4 py-8">
	<div class="mb-6">
		<h2 class="mb-2 text-2xl font-semibold text-gray-800">Registro de IPs</h2>
		<p class="text-gray-600">Haz clic para registrar tu IP actual</p>
	</div>

	<button
		on:click={registerIP}
		class="mb-4 rounded-full bg-cyan-500 px-6 py-2 text-white hover:bg-cyan-600"
	>
		Registrar mi IP
	</button>

	{#if ip}
		<div class="mb-4 rounded-lg bg-green-100 p-3 text-green-700">
			IP registrada: <strong>{ip}</strong> a las <strong>{timestamp}</strong>
		</div>
	{/if}

	{#if error}
		<div class="mb-4 rounded-lg bg-red-100 p-3 text-red-700">
			{error}
		</div>
	{/if}

	<h3 class="mb-2 mt-6 text-lg font-semibold">Historial de registros:</h3>
	<div class="max-h-[300px] overflow-auto rounded-lg border bg-gray-50 p-4">
		{#if records.length > 0}
			<ul class="space-y-1 text-sm text-gray-700">
				{#each records as line}
					<li>{line}</li>
				{/each}
			</ul>
		{:else}
			<p class="text-gray-500">No hay registros aún.</p>
		{/if}
	</div>
</main>

<Footer />
