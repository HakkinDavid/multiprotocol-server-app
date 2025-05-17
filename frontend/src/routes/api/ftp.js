import { PUBLIC_BACKEND_URL } from "$env/static/public";

export async function uploadFile(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${PUBLIC_BACKEND_URL}/ftp/upload`, {
        method: 'POST',
        body: formData
    });

    return response.json();
}
