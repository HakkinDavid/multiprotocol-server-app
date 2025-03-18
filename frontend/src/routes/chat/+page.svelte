<script>
	import { onMount } from 'svelte';
	import { messages, connectWebSocket, sendMessage } from '$lib/stores/chat';

	let newMessage = '';

	onMount(() => {
		connectWebSocket();
	});

	function handleSend() {
		if (newMessage.trim()) {
			sendMessage(newMessage);
			newMessage = '';
		}
	}
</script>

<input
	bind:value={newMessage}
	on:keydown={(e) => e.key === 'Enter' && handleSend()}
	placeholder="Escribe un mensaje..."
/>
<button on:click={handleSend}>Enviar</button>

<ul>
	{#each $messages as msg}
		<li>{msg}</li>
	{/each}
</ul>
