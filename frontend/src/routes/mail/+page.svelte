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
			message = 'Fill in all required fields';
			return;
		}

		const userEmail = getCookie('userEmail');
		if (!userEmail) {
			message = 'User email not found. Please register first.';
			return;
		}

		const mailData = {
			...mail,
			from: userEmail
		};

		const res = await fetch(`${PUBLIC_BACKEND_URL}/mail`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(mailData)
		});

		const data = await res.json();
		message = data.message || 'Failed to send';
		mail = { to: '', subject: '', body: '' };
		await loadInbox();
	}

	function getCookie(name) {
		const value = `; ${document.cookie}`;
		const parts = value.split(`; ${name}=`);
		if (parts.length === 2) return parts.pop()?.split(';').shift();
	}

	async function loadInbox() {
		const res = await fetch(`${PUBLIC_BACKEND_URL}/mail`);
		const data = await res.json();
		inbox = data.messages || [];
	}

	onMount(loadInbox);
</script>

<Header title="Mail ✉️" />

<main class="container mx-auto min-h-[calc(100vh-200px)] px-4 py-8">
	<h2 class="mb-4 text-2xl font-semibold text-gray-800">Compose</h2>

	<div class="mb-6 space-y-4 rounded-lg bg-white p-4 shadow">
		<div>
			<label class="mb-1 block text-sm text-gray-700">To:</label>
			<input class="w-full rounded border px-3 py-2" bind:value={mail.to} />
		</div>
		<div>
			<label class="mb-1 block text-sm text-gray-700">Subject:</label>
			<input class="w-full rounded border px-3 py-2" bind:value={mail.subject} />
		</div>
		<div>
			<label class="mb-1 block text-sm text-gray-700">Body:</label>
			<textarea class="h-32 w-full rounded border px-3 py-2" bind:value={mail.body}></textarea>
		</div>
		<button
			on:click={sendMail}
			class="rounded-full bg-orange-500 px-4 py-2 text-sm text-white hover:bg-orange-600"
		>
			Send
		</button>
		{#if message}
			<p class="text-sm text-gray-600">{message}</p>
		{/if}
	</div>

	<div class="max-h-[400px] overflow-y-auto rounded-lg border bg-gray-50 p-4">
		<h3 class="mb-2 text-lg font-semibold">Inbound mail</h3>
		{#if inbox.length > 0}
			<ul class="space-y-3">
				{#each inbox as mail}
					<li class="rounded border bg-white p-3">
						<p><strong>From:</strong> {mail.from}</p>
						<p><strong>Subject:</strong> {mail.subject}</p>
						<p class="mt-2 whitespace-pre-wrap text-sm text-gray-600">{mail.body}</p>
					</li>
				{/each}
			</ul>
		{:else}
			<p class="text-gray-500">The are no mails currently available...</p>
		{/if}
	</div>
</main>

<Footer />
