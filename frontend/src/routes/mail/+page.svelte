<script>
    let to = '';
    let subject = '';
    let body = '';
    let responseMessage = '';
  
    async function sendMail() {
      const res = await fetch('http://localhost:8000/mail/send', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({to, subject, body})
      });
      const data = await res.json();
      responseMessage = data.message;
    }
  </script>
  
  <h1>Send Email</h1>
  <div>
    <label>To: <input type="email" bind:value={to} /></label>
  </div>
  <div>
    <label>Subject: <input type="text" bind:value={subject} /></label>
  </div>
  <div>
    <label>Body:</label>
    <textarea bind:value={body}></textarea>
  </div>
  <button on:click={sendMail}>Send Email</button>
  <p>{responseMessage}</p>
  