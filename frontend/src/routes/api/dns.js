export async function registerDNS(name, ip) {
    const response = await fetch('http://localhost:8000/dns/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, ip }),
    });
    return response.json();
}

export async function registerSelf() {
    const response = await fetch('http://localhost:8000/dns/auto', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ machine_name: 'laptop', ip_address: '192.168.1.1' }),
    });
    return response.json();
}

export async function fetchDNSRecords() {
    const response = await fetch('http://localhost:8000/dns/records');
    return response.json();
}