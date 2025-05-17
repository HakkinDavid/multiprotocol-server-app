import { PUBLIC_BACKEND_URL } from "$env/static/public";

import { json } from '@sveltejs/kit';

export async function GET() {
  try {
    const response = await fetch(`${PUBLIC_BACKEND_URL}/streaming/list`);
    const data = await response.json();
    return json(data);
  } catch (error) {
    console.error('Error fetching streaming list:', error);
    return json({ files: [] }, { status: 500 });
  }
} 