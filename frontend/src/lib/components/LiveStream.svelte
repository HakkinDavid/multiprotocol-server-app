<script>
  import { PUBLIC_BACKEND_URL, PUBLIC_WS_URL } from '$env/static/public';
  import { onMount, onDestroy } from 'svelte';
  // Streaming en vivo
  let streamActive = false;
  let streamConnecting = false;
  let streamId = `stream-${Math.random().toString(36).substring(2, 9)}`;
  let streamSocket;
  let videoElement;
  let mediaStream;
  let mediaRecorder;
  let recordedChunks = [];
  let streamStatus = 'Desconectado';
  
  // Para ver streams
  let viewStreamId = '';
  let viewStreamActive = false;
  let viewStreamConnecting = false;
  let viewStreamSocket;
  let viewVideoElement;
  let viewStreamStatus = 'Desconectado';
  let receivedFrames = 0;
  // Iniciar streaming en vivo (transmisión)
  async function startLiveStream() {
    try {
      streamConnecting = true;
      streamStatus = 'Solicitando permisos de cámara/micrófono...';
      errorMessage = '';
      
      // Solicitar acceso a la cámara y micrófono
      mediaStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
      });
      
      // Mostrar la vista previa local
      if (videoElement) {
        videoElement.srcObject = mediaStream;
        videoElement.muted = true; // Evitar feedback de audio
      }
      
      streamStatus = 'Conectando al servidor...';
      
      // Crear conexión WebSocket con URL directa al backend
      const wsUrl = `${PUBLIC_WS_URL}/ws/stream/${streamId}`;
      console.log('Conectando a WebSocket:', wsUrl);
      
      // Si ya hay un socket activo, cerrarlo primero
      if (streamSocket && streamSocket.readyState === WebSocket.OPEN) {
        streamSocket.close();
      }
      
      streamSocket = new WebSocket(wsUrl);
      
      streamSocket.onopen = () => {
        streamStatus = 'Conectado! Iniciando transmisión...';
        successMessage = `Stream iniciado con ID: ${streamId}`;
        console.log('WebSocket abierto, comenzando transmisión');
        
        // Enviar un mensaje para indicar que este es un broadcaster
        streamSocket.send(JSON.stringify({ type: 'broadcaster_connected' }));
        
        // Iniciar grabación de media
        const options = { 
          mimeType: 'video/webm; codecs=vp9,opus'
        };
        
        try {
          mediaRecorder = new MediaRecorder(mediaStream, options);
        } catch (e) {
          console.warn('Error con codec VP9, intentando con codec estándar', e);
          mediaRecorder = new MediaRecorder(mediaStream);
        }
        
        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0 && streamSocket.readyState === WebSocket.OPEN) {
            streamSocket.send(event.data);
            recordedChunks.push(event.data);
            streamStatus = 'Transmitiendo...';
          }
        };
        
        // Generar datos cada 100ms para tener un stream fluido
        mediaRecorder.start(100);
        streamActive = true;
        streamConnecting = false;
      };
      
      streamSocket.onmessage = (event) => {
        if (typeof event.data === 'string') {
          try {
            const message = JSON.parse(event.data);
            console.log('Mensaje recibido:', message);
            if (message.type === 'viewer_connected') {
              successMessage = 'Un espectador se ha conectado al stream';
              console.log('Espectador conectado');
            } else if (message.type === 'connection_established') {
              console.log('Conexión establecida con el servidor:', message);
              successMessage = 'Conexión establecida con el servidor';
            }
          } catch (e) {
            console.log('Recibido mensaje de texto:', event.data);
          }
        }
      };
      
      streamSocket.onclose = (event) => {
        console.log('WebSocket cerrado:', event);
        streamStatus = `Desconectado (código: ${event.code})`;
        if (streamActive) {
          if (event.code === 1006) {
            errorMessage = 'La conexión con el servidor se cerró inesperadamente. Intenta de nuevo.';
          } else if (event.code === 1000) {
            successMessage = 'Transmisión finalizada correctamente';
          } else {
            errorMessage = `La conexión con el servidor se ha cerrado (código: ${event.code})`;
          }
          stopLiveStream();
        }
      };
      
      streamSocket.onerror = (error) => {
        console.error('Error en WebSocket:', error);
        errorMessage = 'Error en la conexión de streaming';
        streamStatus = 'Error de conexión';
        streamConnecting = false;
        stopLiveStream();
      };
      
    } catch (err) {
      console.error('Error al iniciar streaming:', err);
      errorMessage = 'Error al acceder a la cámara o micrófono';
      streamStatus = 'Error: no se pudo acceder a la cámara/micrófono';
      streamConnecting = false;
    }
  }
  
  // Detener streaming en vivo
  function stopLiveStream() {
    streamStatus = 'Deteniendo transmisión...';
    
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }
    
    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop());
    }
    
    if (streamSocket && streamSocket.readyState === WebSocket.OPEN) {
      streamSocket.close();
    }
    
    streamActive = false;
    if (videoElement) {
      videoElement.srcObject = null;
    }
    
    streamStatus = 'Desconectado';
    console.log('Transmisión detenida');
    
    // Opcional: guardar la grabación como un archivo nuevo
    if (recordedChunks.length > 0) {
      const blob = new Blob(recordedChunks, { type: 'video/webm' });
      recordedChunks = [];
      
      // Podrías implementar aquí una función para subir el blob grabado al servidor
      // saveRecording(blob);
    }
  }
  
  // Ver un stream en vivo
  function viewLiveStream() {
    if (!viewStreamId) {
      errorMessage = 'Debes ingresar un ID de stream para ver';
      return;
    }
    
    try {
      viewStreamConnecting = true;
      viewStreamStatus = 'Conectando al stream...';
      errorMessage = '';
      receivedFrames = 0;
      
      // Crear WebSocket para ver el stream usando la URL correcta del backend
      const wsUrl = `${PUBLIC_WS_URL}/ws/stream/${viewStreamId}`;
      console.log('Conectando a stream:', wsUrl);
      
      // Si ya hay un socket activo, cerrarlo primero
      if (viewStreamSocket && viewStreamSocket.readyState === WebSocket.OPEN) {
        viewStreamSocket.close();
      }
      
      viewStreamSocket = new WebSocket(wsUrl);
      
      // Crear MediaSource para manejo eficiente de video
      const mediaSource = new MediaSource();
      let sourceBuffer = null;
      
      if (viewVideoElement) {
        viewVideoElement.src = URL.createObjectURL(mediaSource);
      }
      
      mediaSource.addEventListener('sourceopen', () => {
        // Crear SourceBuffer cuando MediaSource esté abierto
        try {
          sourceBuffer = mediaSource.addSourceBuffer('video/webm; codecs="vp8,opus"');
        } catch (e) {
          console.error('Error al crear SourceBuffer:', e);
          errorMessage = 'Error al inicializar reproductor de video';
        }
      });
      
      viewStreamSocket.onopen = () => {
        viewStreamActive = true;
        viewStreamConnecting = false;
        viewStreamStatus = 'Conectado, esperando datos...';
        console.log('Conexión establecida con el stream');
        successMessage = `Conectado al stream: ${viewStreamId}`;
        
        // Enviar un mensaje de ping para registrarse como espectador
        viewStreamSocket.send(JSON.stringify({ type: 'viewer_connected' }));
      };
      
      let blobParts = [];
      
      viewStreamSocket.onmessage = (event) => {
        // Procesar los diferentes tipos de mensajes recibidos
        if (typeof event.data === 'string') {
          try {
            const message = JSON.parse(event.data);
            console.log('Mensaje recibido:', message);
            if (message.type === 'stream_status') {
              viewStreamStatus = message.status;
            } else if (message.type === 'connection_established') {
              viewStreamStatus = 'Conectado al servidor, esperando transmisión...';
              console.log('Conexión establecida con el servidor:', message);
            }
          } catch (e) {
            console.log('Recibido mensaje de texto:', event.data);
          }
          return;
        }
        
        // Procesar datos binarios (frames de video)
        receivedFrames++;
        viewStreamStatus = `Reproduciendo (frames recibidos: ${receivedFrames})`;
        
        // Procesar datos binarios para reproducción de video
        event.data.arrayBuffer().then(buffer => {
          if (sourceBuffer && !sourceBuffer.updating) {
            try {
              sourceBuffer.appendBuffer(buffer);
            } catch (e) {
              console.error('Error al añadir buffer al sourceBuffer:', e);
            }
          } else {
            // Si mediaSource no está listo, almacenar datos para procesamiento posterior
            blobParts.push(buffer);
            
            // Reproducción alternativa con método simple si MediaSource falla
            if (receivedFrames % 10 === 0) { // Actualizar cada 10 frames para reducir carga
              const blob = new Blob([...blobParts], { type: 'video/webm' });
              
              if (viewVideoElement) {
                const currentTime = viewVideoElement.currentTime;
                const wasPlaying = !viewVideoElement.paused;
                
                // Si no estamos usando MediaSource, actualizar src directamente
                if (viewVideoElement.src.startsWith('blob:')) {
                  URL.revokeObjectURL(viewVideoElement.src);
                }
                
                viewVideoElement.src = URL.createObjectURL(blob);
                
                if (wasPlaying) {
                  viewVideoElement.currentTime = currentTime;
                  viewVideoElement.play().catch(e => console.error('Error al reproducir:', e));
                }
              }
            }
          }
        });
      };
      
      viewStreamSocket.onclose = (event) => {
        console.log('Conexión al stream cerrada:', event);
        viewStreamStatus = `Desconectado (código: ${event.code})`;
        if (viewStreamActive) {
          if (receivedFrames === 0) {
            if (event.code === 1006) {
              errorMessage = 'Error de conexión con el servidor. Verifica que el ID sea correcto y que el streamer esté activo.';
            } else {
              errorMessage = 'No se recibieron datos del stream. Verifica el ID del stream.';
            }
          } else if (event.code === 1000) {
            successMessage = 'Transmisión finalizada correctamente';
          } else {
            errorMessage = `La conexión con el stream se ha cerrado (código: ${event.code})`;
          }
          stopViewingStream();
        }
      };
      
      viewStreamSocket.onerror = (error) => {
        console.error('Error al conectar al stream:', error);
        errorMessage = 'Error en la conexión al stream en vivo';
        viewStreamStatus = 'Error de conexión';
        viewStreamConnecting = false;
        stopViewingStream();
      };
      
    } catch (err) {
      console.error('Error al ver stream:', err);
      errorMessage = 'Error al conectar con el stream en vivo';
      viewStreamStatus = 'Error de conexión';
      viewStreamConnecting = false;
    }
  }
  
  // Detener la visualización de un stream
  function stopViewingStream() {
    viewStreamStatus = 'Cerrando conexión...';
    
    if (viewStreamSocket && viewStreamSocket.readyState === WebSocket.OPEN) {
      viewStreamSocket.close();
    }
    
    if (viewVideoElement) {
      if (viewVideoElement.src.startsWith('blob:')) {
        URL.revokeObjectURL(viewVideoElement.src);
      }
      viewVideoElement.src = '';
    }
    
    viewStreamActive = false;
    viewStreamConnecting = false;
    viewStreamStatus = 'Desconectado';
    console.log('Visualización detenida');
  }
onDestroy(() => {
    // Asegurarse de limpiar recursos al salir
    if (streamActive) stopLiveStream();
    if (viewStreamActive) stopViewingStream();
  });
</script>

<!-- Sección de streaming en vivo -->
  <div class="bg-white shadow-md rounded p-6 mb-6">
    <h2 class="text-xl font-semibold text-gray-800 mb-4">Streaming en vivo</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Transmitir stream -->
      <div class="border p-4 rounded">
        <h3 class="font-medium mb-2">Transmitir desde mi cámara</h3>
        
        <!-- Estado de la transmisión -->
        <div class="flex items-center mb-2">
          <div class="w-3 h-3 rounded-full mr-2 {streamActive ? 'bg-green-500 animate-pulse' : streamConnecting ? 'bg-yellow-500' : 'bg-red-500'}"></div>
          <span class="text-sm {streamActive ? 'text-green-700' : streamConnecting ? 'text-yellow-700' : 'text-red-700'}">
            Estado: {streamStatus}
          </span>
        </div>
        
        <p class="text-sm text-gray-600 mb-3">
          ID del stream: <span class="font-mono bg-gray-100 px-1">{streamId}</span>
          <button 
            class="text-blue-500 ml-2" 
            on:click={() => {
              navigator.clipboard.writeText(streamId);
              successMessage = 'ID copiado al portapapeles';
            }}
          >
            Copiar
          </button>
        </p>
        
        <div class="aspect-video bg-gray-900 mb-3 rounded overflow-hidden">
          <video 
            bind:this={videoElement} 
            autoplay 
            playsinline 
            class="w-full h-full"
          ></video>
        </div>
        
        {#if !streamActive && !streamConnecting}
          <button 
            on:click={startLiveStream}
            class="bg-red-500 hover:bg-red-600 text-white py-2 px-4 rounded w-full"
          >
            Iniciar transmisión
          </button>
        {:else if streamConnecting}
          <button 
            disabled
            class="bg-yellow-500 text-white py-2 px-4 rounded w-full opacity-70 cursor-not-allowed"
          >
            Conectando...
          </button>
        {:else}
          <button 
            on:click={stopLiveStream}
            class="bg-gray-700 hover:bg-gray-800 text-white py-2 px-4 rounded w-full"
          >
            Detener transmisión
          </button>
        {/if}
      </div>
      
      <!-- Ver stream -->
      <div class="border p-4 rounded">
        <h3 class="font-medium mb-2">Ver transmisión en vivo</h3>
        
        <!-- Estado de visualización -->
        <div class="flex items-center mb-2">
          <div class="w-3 h-3 rounded-full mr-2 {viewStreamActive ? 'bg-green-500 animate-pulse' : viewStreamConnecting ? 'bg-yellow-500' : 'bg-red-500'}"></div>
          <span class="text-sm {viewStreamActive ? 'text-green-700' : viewStreamConnecting ? 'text-yellow-700' : 'text-red-700'}">
            Estado: {viewStreamStatus}
          </span>
        </div>
        
        <div class="flex space-x-2 mb-3">
          <input 
            type="text" 
            bind:value={viewStreamId}
            placeholder="Introduce ID del stream"
            class="border p-2 rounded flex-1"
          />
          {#if !viewStreamActive && !viewStreamConnecting}
            <button 
              on:click={viewLiveStream}
              disabled={!viewStreamId}
              class="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded disabled:opacity-50"
            >
              Ver
            </button>
          {:else if viewStreamConnecting}
            <button 
              disabled
              class="bg-yellow-500 text-white py-2 px-4 rounded opacity-70 cursor-not-allowed"
            >
              Conectando...
            </button>
          {:else}
            <button 
              on:click={stopViewingStream}
              class="bg-gray-700 hover:bg-gray-800 text-white py-2 px-4 rounded"
            >
              Detener
            </button>
          {/if}
        </div>
        
        <div class="aspect-video bg-gray-900 rounded overflow-hidden">
          <video 
            bind:this={viewVideoElement} 
            autoplay 
            playsinline 
            controls
            class="w-full h-full"
          ></video>
        </div>
      </div>
    </div>
  </div>