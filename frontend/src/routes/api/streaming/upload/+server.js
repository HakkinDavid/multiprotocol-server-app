import { PUBLIC_BACKEND_URL } from "$env/static/public";
import { json } from '@sveltejs/kit';

export async function POST({ request }) {
  try {
    // Obtener el archivo de la solicitud
    const formData = await request.formData();
    
    // Reenviar la solicitud al backend
    const response = await fetch(`${PUBLIC_BACKEND_URL}/streaming/upload`, {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    return json(data);
  } catch (error) {
    console.error('Error uploading file:', error);
    return json(
      { error: 'Error al subir el archivo' }, 
      { status: 500 }
    );
  }
} 