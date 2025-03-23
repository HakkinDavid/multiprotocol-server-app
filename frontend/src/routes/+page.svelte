<script>
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { goto } from '$app/navigation';
</script>

<Header title="Server Management" />

<main>
	<button
		on:click={() => {
			goto('/dns');
		}}
		class="m-4 cursor-pointer rounded-lg bg-cyan-500 px-4 hover:bg-cyan-200"
	>
		DNS
	</button>
	<button
		on:click={() => {
			goto('/web');
		}}
		class="m-4 cursor-pointer rounded-lg bg-green-500 px-4 hover:bg-green-200"
	>
		Web
	</button>
	<button
		on:click={() => {
			goto('/streaming');
		}}
		class="m-4 cursor-pointer rounded-lg bg-red-500 px-4 hover:bg-red-200"
	>
		Streaming
	</button>
	<button
		on:click={() => {
			goto('/mail');
		}}
		class="m-4 cursor-pointer rounded-lg bg-orange-500 px-4 hover:bg-orange-200"
	>
		Mail
	</button>
	<button
		on:click={() => {
			goto('/ftp');
		}}
		class="m-4 cursor-pointer rounded-lg bg-purple-500 px-4 hover:bg-purple-200"
	>
		FTP
	</button>
	<button
		on:click={() => {
			goto('/chat');
		}}
		class="m-4 cursor-pointer rounded-lg bg-pink-500 px-4 hover:bg-pink-200"
	>
		Chat
	</button>
</main>

<Footer />
