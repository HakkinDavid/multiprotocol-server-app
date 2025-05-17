import { PUBLIC_BACKEND_URL } from "$env/static/public";

export async function GET({ params, request }) {
  try {
    const filename = params.filename;
    
    // Reenviar la solicitud al backend incluyendo los headers Range
    const headers = new Headers();
    if (request.headers.has('Range')) {
      headers.set('Range', request.headers.get('Range'));
    }
    
    const response = await fetch(`${PUBLIC_BACKEND_URL}/streaming/play/${filename}`, {
      headers
    });
    
    // Crear una respuesta que incluya todos los headers originales
    const body = await response.arrayBuffer();
    const newResponse = new Response(body);
    
    // Copiar todos los headers de la respuesta original
    response.headers.forEach((value, key) => {
      newResponse.headers.set(key, value);
    });
    
    return newResponse;
  } catch (error) {
    console.error('Error fetching streaming content:', error);
    return new Response('Error al obtener el contenido multimedia', { status: 500 });
  }
} 