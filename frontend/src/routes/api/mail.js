export async function sendEmail(mailData) {
    const response = await fetch('http://localhost:8000/mail/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mailData),
    });
    return response.json();
}