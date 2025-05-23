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
	let loading = false;

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
		try {
			loading = true;
			const userEmail = getCookie('userEmail');
			if (!userEmail) {
				message = 'User email not found. Please register first.';
				return;
			}

			const res = await fetch(`${PUBLIC_BACKEND_URL}/mail?user_email=${encodeURIComponent(userEmail)}`);
			const data = await res.json();
			inbox = data.emails || [];
		} catch (error) {
			message = 'Error loading inbox: ' + (error instanceof Error ? error.message : String(error));
		} finally {
			loading = false;
		}
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

	<div class="max-h-[600px] overflow-y-auto rounded-lg border bg-gray-50 p-4">
		<div class="mb-4 flex items-center justify-between">
			<h3 class="text-lg font-semibold">Inbound mail</h3>
			<button
				on:click={loadInbox}
				class="rounded-full bg-blue-500 px-3 py-1 text-sm text-white hover:bg-blue-600"
			>
				Refresh
			</button>
		</div>
		{#if loading}
			<div class="flex items-center justify-center py-8">
				<div class="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"></div>
				<span class="ml-2 text-gray-600">Loading emails...</span>
			</div>
		{:else if inbox.length > 0}
			<ul class="space-y-3">
				{#each inbox as email}
					<li class="rounded border bg-white p-4 shadow-sm hover:shadow-md transition-shadow">
						<div class="flex justify-between items-start mb-2">
							<h4 class="font-semibold text-gray-800">{email.subject}</h4>
							<span class="text-sm text-gray-500">{email.date}</span>
						</div>
						<p class="text-sm text-gray-600 mb-2"><span class="font-medium">From:</span> {email.from}</p>
						<div class="mt-2 text-sm text-gray-700 whitespace-pre-wrap border-t pt-2">
							{email.body}
						</div>
					</li>
				{/each}
			</ul>
		{:else}
			<p class="text-center text-gray-500 py-8">No emails available...</p>
		{/if}
	</div>
</main>

<Footer />
