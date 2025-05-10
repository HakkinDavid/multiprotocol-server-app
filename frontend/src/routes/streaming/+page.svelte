<script>
    import { onMount, onDestroy } from 'svelte';
    import Header from '$lib/components/Header.svelte';
    import Footer from '$lib/components/Footer.svelte';
    
    let streamingFiles = [];
    let statusData = { status: 'unknown' };
    let loading = true;
    let error = null;
    let success = null;
    let selectedFile = null;
    let fileInput;
    let currentPlaying = null;
    let refreshInterval;
    
    async function loadStatus() {
        try {
            const res = await fetch('http://localhost:8000/streaming/status');
            if (!res.ok) throw new Error("Failed to fetch streaming status");
            statusData = await res.json();
        } catch (err) {
            console.error("Error loading streaming status:", err);
            error = err.message || "Error loading streaming status";
            setTimeout(() => error = null, 3000);
        }
    }
    
    async function loadFiles() {
        loading = true;
        try {
            const res = await fetch('http://localhost:8000/streaming/files');
            if (!res.ok) throw new Error("Failed to fetch streaming files");
            const data = await res.json();
            streamingFiles = data.files || [];
        } catch (err) {
            console.error("Error loading streaming files:", err);
            error = err.message || "Error loading streaming files";
            setTimeout(() => error = null, 3000);
        } finally {
            loading = false;
        }
    }
    
    async function startStreaming(fileName) {
        try {
            const res = await fetch('http://localhost:8000/streaming/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ file_name: fileName })
            });
            
            if (!res.ok) throw new Error("Failed to start streaming");
            
            const data = await res.json();
            success = data.message;
            setTimeout(() => success = null, 3000);
            
            currentPlaying = fileName;
            await loadStatus();
        } catch (err) {
            console.error("Error starting streaming:", err);
            error = err.message || "Error starting streaming";
            setTimeout(() => error = null, 3000);
        }
    }
    
    async function stopStreaming() {
        try {
            const res = await fetch('http://localhost:8000/streaming/stop', {
                method: 'POST'
            });
            
            if (!res.ok) throw new Error("Failed to stop streaming");
            
            const data = await res.json();
            success = data.message;
            setTimeout(() => success = null, 3000);
            
            currentPlaying = null;
            await loadStatus();
        } catch (err) {
            console.error("Error stopping streaming:", err);
            error = err.message || "Error stopping streaming";
            setTimeout(() => error = null, 3000);
        }
    }
    
    async function uploadFile() {
        if (!selectedFile) {
            error = "Please select a file to upload";
            setTimeout(() => error = null, 3000);
            return;
        }
        
        // Check if the file is a valid media file
        const validExtensions = ['.mp4', '.webm', '.ogg', '.mp3', '.wav', '.flac', '.mov'];
        const fileExt = selectedFile.name.substring(selectedFile.name.lastIndexOf('.')).toLowerCase();
        
        if (!validExtensions.includes(fileExt)) {
            error = "Please upload a valid media file (MP4, WebM, OGG, MP3, WAV, FLAC, MOV)";
            setTimeout(() => error = null, 3000);
            return;
        }
        
        // Upload the file
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        try {
            const response = await fetch('http://localhost:8000/streaming/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) throw new Error("Failed to upload file");
            
            const data = await response.json();
            success = data.message;
            setTimeout(() => success = null, 3000);
            
            // Reset the file input
            if (fileInput) fileInput.value = '';
            selectedFile = null;
            
            // Reload the file list
            await loadFiles();
        } catch (err) {
            console.error("Error uploading file:", err);
            error = err.message || "Error uploading file";
            setTimeout(() => error = null, 3000);
        }
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    function formatDate(timestamp) {
        return new Date(timestamp * 1000).toLocaleString();
    }
    
    // Load status and files on mount, and set up refresh interval
    onMount(async () => {
        await Promise.all([loadFiles(), loadStatus()]);
        
        // Refresh status every 5 seconds
        refreshInterval = setInterval(async () => {
            await loadStatus();
        }, 5000);
    });
    
    // Clean up interval on component destruction
    onDestroy(() => {
        if (refreshInterval) clearInterval(refreshInterval);
    });
</script>

<Header title="Streaming Service" />

<main class="container mx-auto px-4 py-8 min-h-[calc(100vh-200px)]">
    <div class="mb-8">
        <h2 class="text-2xl font-semibold text-gray-800 mb-2">Media Streaming</h2>
        <p class="text-gray-600">Stream video and audio files from your server</p>
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
    
    <!-- Streaming Status Card -->
    <div class="bg-white rounded-xl shadow p-6 mb-6">
        <div class="flex justify-between items-center">
            <div>
                <h3 class="text-xl font-semibold">Streaming Status</h3>
                <p class="text-gray-600 mt-1">
                    Current status: 
                    {#if statusData.status === 'started'}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            Active
                        </span>
                    {:else}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            Stopped
                        </span>
                    {/if}
                </p>
                {#if statusData.current_file}
                    <p class="text-gray-600 mt-1">Currently streaming: {statusData.current_file}</p>
                {/if}
            </div>
            
            <button 
                on:click={stopStreaming}
                class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors"
                disabled={statusData.status !== 'started'}>
                Stop Streaming
            </button>
        </div>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Media Player -->
        <div class="lg:col-span-2 bg-white rounded-xl shadow p-6">
            <h3 class="text-xl font-semibold mb-4">Media Player</h3>
            
            {#if currentPlaying}
                <div class="aspect-w-16 aspect-h-9 bg-black rounded-lg overflow-hidden">
                    <!-- Determine media type based on file extension -->
                    {#if currentPlaying.toLowerCase().endsWith('.mp3') || currentPlaying.toLowerCase().endsWith('.wav') || currentPlaying.toLowerCase().endsWith('.flac')}
                        <audio 
                            controls 
                            autoplay 
                            class="w-full" 
                            src={`http://localhost:8000/streaming/play/${currentPlaying}`}>
                            Your browser does not support the audio element.
                        </audio>
                    {:else}
                        <video 
                            controls 
                            autoplay 
                            class="w-full h-full object-contain" 
                            src={`http://localhost:8000/streaming/play/${currentPlaying}`}>
                            Your browser does not support the video element.
                        </video>
                    {/if}
                </div>
                <p class="mt-2 text-center text-gray-700">Now playing: {currentPlaying}</p>
            {:else}
                <div class="aspect-w-16"></div>
            {/if}
        </div>
    </div>
</main>