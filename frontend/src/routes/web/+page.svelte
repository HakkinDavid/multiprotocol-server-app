<script>
    import { onMount } from 'svelte';
    let content = '';
  
    async function loadContent() {
      const res = await fetch('http://localhost:8000/web/content');
      const data = await res.json();
      content = data.content;
    }
  
    onMount(loadContent);
  </script>
  
  <h1>Web Content</h1>
  <div>{@html content}</div>
  