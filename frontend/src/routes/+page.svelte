<script>
    import Header from '$lib/components/Header.svelte';
    import Footer from '$lib/components/Footer.svelte';
    import {goto} from '$app/navigation';
    
    const services = [
        { name: 'DNS', path: '/dns', icon: '🌐', color: 'bg-cyan-500', hoverColor: 'bg-cyan-600', description: 'Gestión de nombres de dominio' },
        { name: 'Web', path: '/web', icon: '🖥️', color: 'bg-green-500', hoverColor: 'bg-green-600', description: 'Servidor web HTTP/HTTPS' },
        { name: 'Streaming', path: '/streaming', icon: '📺', color: 'bg-red-500', hoverColor: 'bg-red-600', description: 'Servicio de streaming de contenido' },
        { name: 'Mail', path: '/mail', icon: '✉️', color: 'bg-orange-500', hoverColor: 'bg-orange-600', description: 'Servidor de correo electrónico' },
        { name: 'FTP', path: '/ftp', icon: '📁', color: 'bg-purple-500', hoverColor: 'bg-purple-600', description: 'Transferencia de archivos' }
    ];
</script>

<Header title="Multiprotocol Server Management" />

<main class="container mx-auto px-4 py-8 min-h-[calc(100vh-200px)]">
    <div class="mb-8">
        <h2 class="text-2xl font-semibold text-gray-800 mb-2">Panel de Control</h2>
        <p class="text-gray-600">Selecciona un servicio para configurar y gestionar</p>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each services as service}
            <div 
                class="rounded-xl shadow-md overflow-hidden transition-all hover:shadow-lg cursor-pointer transform hover:-translate-y-1"
                on:click={() => {goto(service.path)}}
            >
                <div class="{service.color} p-6 text-white">
                    <div class="flex items-center">
                        <span class="text-4xl mr-4">{service.icon}</span>
                        <div>
                            <h3 class="text-xl font-bold">{service.name}</h3>
                            <p class="text-sm opacity-90">{service.description}</p>
                        </div>
                    </div>
                </div>
                <div class="bg-white p-4">
                    <p class="text-sm text-gray-600">Configurar servicio {service.name}</p>
                    <button class="mt-2 px-4 py-1 rounded-full bg-gray-100 text-gray-800 text-sm hover:bg-gray-200">
                        Acceder →
                    </button>
                </div>
            </div>
        {/each}
    </div>
</main>

<Footer />
