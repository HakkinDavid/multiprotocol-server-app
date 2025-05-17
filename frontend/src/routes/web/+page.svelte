<script>
    import { onMount } from 'svelte';
    import { PUBLIC_BACKEND_URL } from '$env/static/public';
    let content = '';
  
    async function loadContent() {
      const res = await fetch(`${PUBLIC_BACKEND_URL}/web/content`);
      const data = await res.json();
      content = data.content;
    }
  
    onMount(loadContent);
  </script>
  
  <h1>Web Content</h1>
  <div>{@html content}</div>
  