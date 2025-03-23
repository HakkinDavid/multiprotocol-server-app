import { writable } from "svelte/store";

export const messages = writable([]);
let socket; 

export function connectWebSocket() {
  socket = new WebSocket("ws://192.168.1.143:8000/ws");

  socket.onopen = function(event) {
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