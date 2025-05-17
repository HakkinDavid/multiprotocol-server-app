import { PUBLIC_BACKEND_URL } from "$env/static/public";

export async function registerDNS(name, ip) {
    const response = await fetch(`${PUBLIC_BACKEND_URL}/dns/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, ip }),
    });
    return response.json();
}

export async function registerSelf() {
    const response = await fetch(`${PUBLIC_BACKEND_URL}/dns/auto`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ machine_name: 'laptop', ip_address: '192.168.1.1' }),
    });
    return response.json();
}

export async function fetchDNSRecords() {
    const response = await fetch(`${PUBLIC_BACKEND_URL}/dns/records`);
    return response.json();
}