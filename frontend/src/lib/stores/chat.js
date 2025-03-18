import { writable } from "svelte/store";

export const messages = writable([]);
let socket; // Declarar socket en el ámbito del módulo

export function connectWebSocket() {
  socket = new WebSocket("ws://localhost:8000/ws"); // Asignar a la variable del módulo

  socket.onopen = function(event) {
    console.log("WebSocket connection established.");
    socket.send("Hello from the client!");
  };

  socket.onmessage = (event) => {
    messages.update((msgs) => [...msgs, event.data]);
  };
}

export function sendMessage(text) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(text);
  }
}