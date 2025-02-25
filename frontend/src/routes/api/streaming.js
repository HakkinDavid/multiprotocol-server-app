export async function startStream() {
    const response = await fetch('http://localhost:8000/streaming/start', {
        method: 'POST'
    });
    return response.json();
}

export async function getStreamingStatus() {
    const response = await fetch('http://localhost:8000/streaming/status');
    return response.json();
}