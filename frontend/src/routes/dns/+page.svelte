<script>
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';

	let ip = '';
	let timestamp = '';
	let records = [];
	let error = '';

	async function registerIP() {
		error = '';
		try {
			const res = await fetch(`${PUBLIC_BACKEND_URL}/dns/register`, { method: 'POST' });
			if (res.status === 409) {
				throw new Error('This IP has already been registered');
			} else if (!res.ok) throw new Error('Error while registering the IP: ' + res.statusText);
			const data = await res.json();
			ip = data.ip;
			timestamp = data.timestamp;
			await fetchRecords();
		} catch (err) {
			error = err.message;
		}
	}

	async function fetchRecords() {
		const res = await fetch(`${PUBLIC_BACKEND_URL}/dns/records`);
		const data = await res.json();
		records = data.records;
	}

	onMount(fetchRecords);
</script>

<Header title="DNS Service 🌐" />

<main class="container mx-auto min-h-[calc(100vh-200px)] px-4 py-8">
	<div class="mb-6">
		<h2 class="mb-2 text-2xl font-semibold text-gray-800">Registered IPs</h2>
		<p class="text-gray-600">Click to register your current IP</p>
	</div>

	<button
		on:click={registerIP}
		class="mb-4 rounded-full bg-cyan-500 px-6 py-2 text-white hover:bg-cyan-600"
	>
		Register my IP
	</button>

	{#if ip}
		<div class="mb-4 rounded-lg bg-green-100 p-3 text-green-700">
			IP registered: <strong>{ip}</strong> at <strong>{timestamp}</strong>
		</div>
	{/if}

	{#if error}
		<div class="mb-4 rounded-lg bg-red-100 p-3 text-red-700">
			{error}
		</div>
	{/if}

	<h3 class="mb-2 mt-6 text-lg font-semibold">Registry</h3>
	<div class="max-h-[300px] overflow-auto rounded-lg border bg-gray-50 p-4">
		{#if records.length > 0}
			<ul class="space-y-1 text-sm text-gray-700">
				{#each records as line}
					<li>{line}</li>
				{/each}
			</ul>
		{:else}
			<p class="text-gray-500">Empty...</p>
		{/if}
	</div>
</main>

<Footer />
