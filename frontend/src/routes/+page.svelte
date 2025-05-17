<script>
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { goto } from '$app/navigation';

	const services = [
		{
			name: 'DNS',
			path: '/dns',
			icon: '🌐',
			color: 'bg-cyan-500',
			hoverColor: 'bg-cyan-600',
			description: 'Domain names management'
		},
		{
			name: 'Web',
			path: '/web',
			icon: '🖥️',
			color: 'bg-green-500',
			hoverColor: 'bg-green-600',
			description: 'Web over HTTP service'
		},
		{
			name: 'Streaming',
			path: '/streaming',
			icon: '📺',
			color: 'bg-red-500',
			hoverColor: 'bg-red-600',
			description: 'Streaming content service'
		},
		{
			name: 'Mail',
			path: '/mail',
			icon: '✉️',
			color: 'bg-orange-500',
			hoverColor: 'bg-orange-600',
			description: 'Electronic mail service'
		},
		{
			name: 'FTP',
			path: '/ftp',
			icon: '📁',
			color: 'bg-purple-500',
			hoverColor: 'bg-purple-600',
			description: 'File transfer protocol service'
		},
		{
			name: 'Chat',
			path: '/chat',
			icon: '💬',
			color: 'bg-blue-500',
			hoverColor: 'bg-blue-600',
			description: 'Real-time chat service'
		}
	];
</script>

<Header title="Multiprotocol Server App" />

<main class="container mx-auto min-h-[calc(100vh-200px)] px-4 py-8">
	<div class="mb-8">
		<h2 class="mb-2 text-2xl font-semibold text-gray-800">Control Panel</h2>
		<p class="text-gray-600">Click on a service and begin enjoying!</p>
	</div>

	<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
		{#each services as service}
			<div
				class="transform cursor-pointer overflow-hidden rounded-xl shadow-md transition-all hover:-translate-y-1 hover:shadow-lg"
				on:click={() => {
					goto(service.path);
				}}
			>
				<div class="{service.color} p-6 text-white">
					<div class="flex items-center">
						<span class="mr-4 text-4xl">{service.icon}</span>
						<div>
							<h3 class="text-xl font-bold">{service.name}</h3>
							<p class="text-sm opacity-90">{service.description}</p>
						</div>
					</div>
				</div>
				<div class="bg-white p-4">
					<button
						class="rounded-full bg-gray-100 px-4 py-1 text-sm text-gray-800 hover:bg-gray-200"
					>
						Access →
					</button>
				</div>
			</div>
		{/each}
	</div>
</main>

<Footer />
