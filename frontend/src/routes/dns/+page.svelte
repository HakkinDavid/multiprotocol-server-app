<script>
    import { onMount } from 'svelte';
    let dnsRecords = [];
    let machineName = '';
    let ipAddress = '';
  
    async function loadRecords() {
      const res = await fetch('http://localhost:8000/dns/records');
      const data = await res.json();
      dnsRecords = data.records;
    }
  
    async function addRecord() {
      // Use the automatic DNS creation endpoint.
      const res = await fetch('http://localhost:8000/dns/auto', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ machine_name: machineName, ip_address: ipAddress })
      });
      const data = await res.json();
      await loadRecords();
      machineName = '';
      ipAddress = '';
    }
  
    onMount(loadRecords);
  </script>
  
  <h1>DNS Records Management</h1>
  
  <table border="1" cellpadding="5">
    <thead>
      <tr>
        <th>Name</th>
        <th>Type</th>
        <th>Value</th>
      </tr>
    </thead>
    <tbody>
      {#each dnsRecords as record}
        <tr>
          <td>{record.name}</td>
          <td>{record.type}</td>
          <td>{record.value}</td>
        </tr>
      {/each}
    </tbody>
  </table>
  
  <h2>Add Automatic DNS Record</h2>
  <div>
    <label>Machine Name: <input type="text" bind:value={machineName} /></label>
  </div>
  <div>
    <label>IP Address: <input type="text" bind:value={ipAddress} /></label>
  </div>
  <button on:click={addRecord}>Add DNS Record</button>
  