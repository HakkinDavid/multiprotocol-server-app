<script>
    import { fly } from "svelte/transition";
</script>
<footer class="bg-gray-800 text-gray-300 py-6 mt-auto" in:fly={{'y': '200', 'duration': 1000, 'delay': 500}}>
    <div class="container mx-auto px-4">
        <div class="flex flex-col md:flex-row justify-between items-center">
            <p>&copy; 2025 David Santana, Hugo Manzano, Oscar Angulo</p>
            <div class="mt-4 md:mt-0">
                <span class="text-sm">Multiprotocol Server App</span>
            </div>
        </div>
    </div>
</footer>
