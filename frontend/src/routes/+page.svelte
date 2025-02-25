<script>
    import Header from '$lib/components/Header.svelte';
    import Footer from '$lib/components/Footer.svelte';
    import {goto} from '$app/navigation';
</script>

<Header title="Server Management" />

<main>
    <button on:click={() => {goto('/dns')}} class="rounded-lg bg-cyan-500 px-4 m-4 hover:bg-cyan-200 cursor-pointer">
        DNS
    </button>
    <button on:click={() => {goto('/web')}} class="rounded-lg bg-green-500 px-4 m-4 hover:bg-green-200 cursor-pointer">
        Web
    </button>
    <button on:click={() => {goto('/streaming')}} class="rounded-lg bg-red-500 px-4 m-4 hover:bg-red-200 cursor-pointer">
        Streaming
    </button>
    <button on:click={() => {goto('/mail')}} class="rounded-lg bg-orange-500 px-4 m-4 hover:bg-orange-200 cursor-pointer">
        Mail
    </button>
    <button on:click={() => {goto('/ftp')}} class="rounded-lg bg-purple-500 px-4 m-4 hover:bg-purple-200 cursor-pointer">
        FTP
    </button>
</main>

<Footer />
