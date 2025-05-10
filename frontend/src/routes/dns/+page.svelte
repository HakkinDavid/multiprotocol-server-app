<script>
    import { onMount } from 'svelte';
    import Header from '$lib/components/Header.svelte';
    import Footer from '$lib/components/Footer.svelte';
    
    let dnsRecords = [];
    let machineName = '';
    let ipAddress = '';
    let loading = true;
    let error = null;
    let success = null;
    
    // Automatically register this client on component mount
    async function registerSelf() {
        try {
            const res = await fetch('http://localhost:8000/dns/auto', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await res.json();
            success = "Client successfully registered with DNS service";
            setTimeout(() => success = null, 3000);
            await loadRecords();
        } catch (err) {
            error = "Failed to register client automatically";
            setTimeout(() => error = null, 3000);
        }
    }
    
    async function loadRecords() {
        loading = true;
        try {
            const res = await fetch('http://localhost:8000/dns/records');
            if (!res.ok) throw new Error("Failed to fetch DNS records");
            const data = await res.json();
            dnsRecords = data.records;
        } catch (err) {
            error = err.message || "Error loading DNS records";
            setTimeout(() => error = null, 3000);
        } finally {
            loading = false;
        }
    }
    
    async function addRecord() {
        if (!machineName || !ipAddress) {
            error = "Machine name and IP address are required";
            setTimeout(() => error = null, 3000);
            return;
        }
        
        try {
            // Use the DNS registration endpoint
            const res = await fetch('http://localhost:8000/dns/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: machineName, ip: ipAddress })
            });
            
            if (!res.ok) throw new Error("Failed to register DNS record");
            
            const data = await res.json();
            success = data.message;
            setTimeout(() => success = null, 3000);
            
            await loadRecords();
            machineName = '';
            ipAddress = '';
        } catch (err) {
            error = err.message || "Error adding DNS record";
            setTimeout(() => error = null, 3000);
        }
    }
    
    async function deleteRecord(name) {
        try {
            const res = await fetch(`http://localhost:8000/dns/records/${name}`, {
                method: 'DELETE'
            });
            
            if (!res.ok) throw new Error(`Failed to delete record ${name}`);
            
            const data = await res.json();
            success = data.message;
            setTimeout(() => success = null, 3000);
            
            await loadRecords();
        } catch (err) {
            error = err.message || "Error deleting DNS record";
            setTimeout(() => error = null, 3000);
        }
    }
    
    // Load records and register self on component mount
    onMount(async () => {
        await loadRecords();
        await registerSelf();
    });
</script>

<Header title="DNS Management" />

<main class="container mx-auto px-4 py-8 min-h-[calc(100vh-200px)]">
    <div class="mb-8">
        <h2 class="text-2xl font-semibold text-gray-800 mb-2">DNS Records Management</h2>
        <p class="text-gray-600">Manage domain names and IP addresses</p>
    </div>
    
    {#if error}
        <div class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6" role="alert">
            <p>{error}</p>
        </div>
    {/if}
    
    {#if success}
        <div class="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-6" role="alert">
            <p>{success}</p>
        </div>
    {/if}
    
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- DNS Records Table -->
        <div class="lg:col-span-2 bg-white rounded-xl shadow p-6">
            <h3 class="text-xl font-semibold mb-4">DNS Records</h3>
            
            {#if loading}
                <div class="flex justify-center items-center py-8">
                    <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
                </div>
            {:else if dnsRecords.length === 0}
                <div class="text-center py-8 text-gray-500">
                    No DNS records found
                </div>
            {:else}
                <div class="overflow-x-auto">
                    <table class="min-w-full bg-white">
                        <thead class="bg-gray-100">
                            <tr>
                                <th class="py-3 px-4 text-left">Name</th>
                                <th class="py-3 px-4 text-left">Type</th>
                                <th class="py-3 px-4 text-left">IP Address</th>
                                <th class="py-3 px-4 text-left">Last Connected</th>
                                <th class="py-3 px-4 text-left">Actions</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200">
                            {#each dnsRecords as record}
                                <tr class="hover:bg-gray-50">
                                    <td class="py-3 px-4">{record.name}</td>
                                    <td class="py-3 px-4">{record.type}</td>
                                    <td class="py-3 px-4">{record.value}</td>
                                    <td class="py-3 px-4">{record.last_connected ? new Date(record.last_connected).toLocaleString() : 'N/A'}</td>
                                    <td class="py-3 px-4">
                                        <button 
                                            on:click={() => deleteRecord(record.name)}
                                            class="text-red-600 hover:text-red-800 transition-colors">
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            {/if}
            
            <div class="mt-4 flex justify-center">
                <button 
                    on:click={loadRecords}
                    class="flex items-center px-4 py-2 bg-blue-50 text-blue-700 rounded-md hover:bg-blue-100 transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
                    </svg>
                    Refresh Records
                </button>
            </div>
        </div>
        
        <!-- Add DNS Record Form -->
        <div class="bg-white rounded-xl shadow p-6">
            <h3 class="text-xl font-semibold mb-4">Add DNS Record</h3>
            <form on:submit|preventDefault={addRecord} class="space-y-4">
                <div>
                    <label for="machineName" class="block text-sm font-medium text-gray-700 mb-1">Machine Name</label>
                    <input 
                        type="text" 
                        id="machineName"
                        bind:value={machineName} 
                        placeholder="Enter machine name" 
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" 
                        required
                    />
                </div>
                
                <div>
                    <label for="ipAddress" class="block text-sm font-medium text-gray-700 mb-1">IP Address</label>
                    <input 
                        type="text" 
                        id="ipAddress"
                        bind:value={ipAddress} 
                        placeholder="Enter IP address"
                        title="Please enter a valid IP address (e.g. 192.168.1.1)"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" 
                        required
                    />
                </div>
                
                <div class="flex justify-end">
                    <button 
                        type="submit" 
                        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors">
                        Add DNS Record
                    </button>
                </div>
            </form>
            
            <div class="mt-6 pt-6 border-t border-gray-200">
                <h4 class="text-lg font-medium mb-2">Auto Registration</h4>
                <p class="text-sm text-gray-600 mb-4">
                    This client has been automatically registered with the DNS service.
                    Click the button below to register again if needed.
                </p>
                <button 
                    on:click={registerSelf}
                    class="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors">
                    Register This Client
                </button>
            </div>
        </div>
    </div>
</main>

<Footer />