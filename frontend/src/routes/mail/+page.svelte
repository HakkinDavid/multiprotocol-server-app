<script>
  import Header from '$lib/components/Header.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { onMount } from 'svelte';

  let mail = {
    to: '',
    subject: '',
    body: ''
  };
  let message = '';
  let inbox = [];

  async function sendMail() {
    if (!mail.to || !mail.subject || !mail.body) {
      message = 'Completa todos los campos.';
      return;
    }

    const res = await fetch('/api/mail/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(mail)
    });

    const data = await res.json();
    message = data.message || 'Envío fallido';
    mail = { to: '', subject: '', body: '' };
    await loadInbox();
  }

  async function loadInbox() {
    const res = await fetch('/api/mail/inbox');
    const data = await res.json();
    inbox = data.messages || [];
  }

  onMount(loadInbox);
</script>

<Header title="Correo ✉️" />

<main class="container mx-auto px-4 py-8 min-h-[calc(100vh-200px)]">
  <h2 class="text-2xl font-semibold text-gray-800 mb-4">Enviar Correo</h2>

  <div class="bg-white rounded-lg p-4 shadow mb-6 space-y-4">
    <div>
      <label class="block text-sm text-gray-700 mb-1">Para:</label>
      <input class="w-full border px-3 py-2 rounded" bind:value={mail.to} />
    </div>
    <div>
      <label class="block text-sm text-gray-700 mb-1">Asunto:</label>
      <input class="w-full border px-3 py-2 rounded" bind:value={mail.subject} />
    </div>
    <div>
      <label class="block text-sm text-gray-700 mb-1">Mensaje:</label>
      <textarea class="w-full border px-3 py-2 rounded h-32" bind:value={mail.body}></textarea>
    </div>
    <button on:click={sendMail} class="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-full text-sm">
      Enviar
    </button>
    {#if message}
      <p class="text-sm text-gray-600">{message}</p>
    {/if}
  </div>

  <div class="bg-gray-50 border rounded-lg p-4 max-h-[400px] overflow-y-auto">
    <h3 class="text-lg font-semibold mb-2">Bandeja de Entrada</h3>
    {#if inbox.length > 0}
      <ul class="space-y-3">
        {#each inbox as mail}
          <li class="border rounded p-3 bg-white">
            <p><strong>De:</strong> {mail.from}</p>
            <p><strong>Asunto:</strong> {mail.subject}</p>
            <p class="text-sm text-gray-600 mt-2 whitespace-pre-wrap">{mail.body}</p>
          </li>
        {/each}
      </ul>
    {:else}
      <p class="text-gray-500">No hay correos.</p>
    {/if}
  </div>
</main>

<Footer />
