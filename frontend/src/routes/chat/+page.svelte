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

<div class="chat-container">
	<div class="chat-header">
		<h2>Chat room</h2>
	</div>

	<div class="chat-messages">
		{#each $messages as msg}
			<div class="message {msg.isSentByClient ? 'sent' : 'received'}">
				<p>{msg.text}</p>
			</div>
		{/each}
	</div>

	<div class="chat-input">
		<input
			bind:value={newMessage}
			on:keydown={(e) => e.key === 'Enter' && handleSend()}
			placeholder="Escribe un mensaje..."
		/>
		<button on:click={handleSend}>Enviar</button>
	</div>
</div>

<style>
	.chat-container {
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		width: 100%;
		max-width: 600px;
		height: 80vh;
		margin: 0 auto;
		border: 1px solid #ddd;
		border-radius: 10px;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
		background-color: #f9f9f9;
		overflow: hidden;
	}

	.chat-header {
		padding: 1rem;
		background-color: #0078ff;
		color: white;
		text-align: center;
		font-size: 1.5rem;
		font-weight: bold;
	}

	.chat-messages {
		display: flex;
		flex-direction: column;
		flex: 1;
		padding: 1rem;
		overflow-y: auto;
		background-color: #e5e5e5;
	}

	.message {
		margin: 0.5rem 0;
		padding: 0.8rem;
		border-radius: 20px;
		max-width: 70%;
		word-wrap: break-word;
	}

	.message.sent {
		background-color: #0078ff;
		color: white;
		align-self: flex-end;
	}

	.message.received {
		background-color: #f1f1f1;
		color: black;
		align-self: flex-start;
	}

	.chat-input {
		display: flex;
		padding: 1rem;
		background-color: white;
		border-top: 1px solid #ddd;
	}

	.chat-input input {
		flex: 1;
		padding: 0.8rem;
		border: 1px solid #ddd;
		border-radius: 20px;
		outline: none;
		font-size: 1rem;
		margin-right: 0.5rem;
	}

	.chat-input button {
		padding: 0.8rem 1.5rem;
		background-color: #0078ff;
		color: white;
		border: none;
		border-radius: 20px;
		cursor: pointer;
		font-size: 1rem;
	}

	.chat-input button:hover {
		background-color: #005bb5;
	}
</style>
