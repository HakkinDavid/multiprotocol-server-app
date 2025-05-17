<script>
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { onMount } from 'svelte';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';

	let mail = {
		to: '',
		subject: '',
		body: ''
	};
	let message = '';
	let inbox = [];

	async function sendMail() {
		if (!mail.to || !mail.subject || !mail.body) {
			message = 'Completa todos los campos.';
			return;
		}

		const res = await fetch(`${PUBLIC_BACKEND_URL}/mail`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(mail)
		});

		const data = await res.json();
		message = data.message || 'Envío fallido';
		mail = { to: '', subject: '', body: '' };
		await loadInbox();
	}

	async function loadInbox() {
		const res = await fetch(`${PUBLIC_BACKEND_URL}/mail/inbox`);
		const data = await res.json();
		inbox = data.messages || [];
	}

	onMount(loadInbox);
</script>

<Header title="Correo ✉️" />

<main class="container mx-auto min-h-[calc(100vh-200px)] px-4 py-8">
	<h2 class="mb-4 text-2xl font-semibold text-gray-800">Enviar Correo</h2>

	<div class="mb-6 space-y-4 rounded-lg bg-white p-4 shadow">
		<div>
			<label class="mb-1 block text-sm text-gray-700">Para:</label>
			<input class="w-full rounded border px-3 py-2" bind:value={mail.to} />
		</div>
		<div>
			<label class="mb-1 block text-sm text-gray-700">Asunto:</label>
			<input class="w-full rounded border px-3 py-2" bind:value={mail.subject} />
		</div>
		<div>
			<label class="mb-1 block text-sm text-gray-700">Mensaje:</label>
			<textarea class="h-32 w-full rounded border px-3 py-2" bind:value={mail.body}></textarea>
		</div>
		<button
			on:click={sendMail}
			class="rounded-full bg-orange-500 px-4 py-2 text-sm text-white hover:bg-orange-600"
		>
			Enviar
		</button>
		{#if message}
			<p class="text-sm text-gray-600">{message}</p>
		{/if}
	</div>

	<div class="max-h-[400px] overflow-y-auto rounded-lg border bg-gray-50 p-4">
		<h3 class="mb-2 text-lg font-semibold">Bandeja de Entrada</h3>
		{#if inbox.length > 0}
			<ul class="space-y-3">
				{#each inbox as mail}
					<li class="rounded border bg-white p-3">
						<p><strong>De:</strong> {mail.from}</p>
						<p><strong>Asunto:</strong> {mail.subject}</p>
						<p class="mt-2 whitespace-pre-wrap text-sm text-gray-600">{mail.body}</p>
					</li>
				{/each}
			</ul>
		{:else}
			<p class="text-gray-500">No hay correos.</p>
		{/if}
	</div>
</main>

<Footer />
