import { writable } from "svelte/store";

export const messages = writable([]);
let socket;
const clientId = Math.random().toString(36).substring(2, 15); // Creates a unique Id

export function connectWebSocket() {
  socket = new WebSocket("ws://localhost:8000/ws");

  socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.clientId !== clientId) {
      messages.update((msgs) => [...msgs, { text: message.text, isSentByClient: false }]);
    }
  };
}

export function sendMessage(text) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    // Message sent by the client
    messages.update((msgs) => [...msgs, { text, isSentByClient: true }]);
    socket.send(JSON.stringify({ text, clientId }));
  }
}