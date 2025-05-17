<script>
    import { goto } from "$app/navigation";
    import { page } from "$app/state";
    import { fly } from "svelte/transition";
    
    export let title = "Server Dashboard";
</script>

<header class="bg-gradient-to-r from-blue-600 to-indigo-800 shadow-lg">
    <div class="container mx-auto px-4 py-6 flex flex-row" in:fly={{ 'x': -200, 'delay': 500, 'duration': 1000 }} out:fly={{ 'x': -200, 'duration': 500 }}>
        {#if page.url.pathname !== '/'}
            <button
                class="rounded-full bg-blue-500 mx-auto my-auto text-sm text-white hover:bg-indigo-800 cursor-pointer w-12 h-12"
                on:click={()=>{goto('/')}}
            >
                ⬅︎
            </button>
        {/if}
        <div class="container mx-auto px-4 py-6">
            <h1 class="text-3xl font-bold text-white">{title}</h1>
            <p class="text-blue-100 mt-1">Gestión de servicios multiprotocolo</p>
        </div>
    </div>
</header>
