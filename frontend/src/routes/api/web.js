import { PUBLIC_BACKEND_URL } from "$env/static/public";

export async function fetchWebConfig() {
    const response = await fetch(`${PUBLIC_BACKEND_URL}/web/content`);
    return response.json();
}
