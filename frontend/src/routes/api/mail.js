import { PUBLIC_BACKEND_URL } from "$env/static/public";

export async function sendEmail(mailData) {
    const response = await fetch(`${PUBLIC_BACKEND_URL}/mail/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mailData),
    });
    return response.json();
}