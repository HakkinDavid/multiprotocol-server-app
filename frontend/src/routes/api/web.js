export async function fetchWebConfig() {
    const response = await fetch('http://localhost:8000/web/content');
    return response.json();
}
