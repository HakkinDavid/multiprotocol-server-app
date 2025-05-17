import os
import shutil
import asyncio
import smtplib
from email.mime.text import MIMEText
from typing import List
import json

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, WebSocket, WebSocketDisconnect, Request

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.auth import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user

from fastapi.responses import FileResponse, StreamingResponse, Response
import time
import aiofiles
import os.path
from pathlib import Path


# Routes imports
#from app.routes.chat import router as chat_router

router = APIRouter()

# ============================
# User Management Endpoints
# ============================

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute("SELECT * FROM users WHERE username = :username", {"username": user.username})
    if result.fetchone():
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_pwd = hash_password(user.password)
    await db.execute(
        "INSERT INTO users (username, hashed_password) VALUES (:username, :password)",
        {"username": user.username, "password": hashed_pwd}
    )
    await db.commit()
    return UserResponse(id=1, username=user.username)

@router.post("/login")
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute("SELECT * FROM users WHERE username = :username", {"username": user.username})
    user_record = result.fetchone()
    if not user_record or not verify_password(user.password, user_record.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user

# =======================================
# Multiprotocol Endpoints Implementation
# =======================================


# --- Web Service ---
WEB_CONTENT_FILE = "web/index.html"

@router.get("/web/content")
async def get_web_content():
    if not os.path.exists(WEB_CONTENT_FILE):
        return {"content": ""}
    with open(WEB_CONTENT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    return {"content": content}

@router.post("/web/deploy")
async def deploy_web(content: dict):
    if "html" not in content:
        raise HTTPException(status_code=400, detail="Missing HTML content")
    with open(WEB_CONTENT_FILE, "w", encoding="utf-8") as f:
        f.write(content["html"])
    return {"message": "Web content deployed"}

# --- Mail Service ---
@router.post("/mail/send")
async def send_mail(mail_data: dict):
    required_keys = {"to", "subject", "body"}
    if not required_keys.issubset(mail_data.keys()):
        raise HTTPException(status_code=400, detail="Missing required mail fields")
    try:
        # For testing, run a debug SMTP server:
        # python -m smtpd -c DebuggingServer -n localhost:1025
        smtp_server = "localhost"
        smtp_port = 1025
        msg = MIMEText(mail_data["body"])
        msg["Subject"] = mail_data["subject"]
        msg["From"] = "no-reply@example.com"
        msg["To"] = mail_data["to"]
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mail sending failed: {e}")
    return {"message": "Mail sent", "details": mail_data}

# --- FTP Service ---
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/ftp/upload")
async def upload_ftp(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"message": "File uploaded", "filename": file.filename}

@router.get("/ftp/list")
async def list_ftp_files():
    files = os.listdir(UPLOAD_DIR)
    return {"files": files}

# --- Chat ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str, websocket):
        for connection in self.active_connections:
            if connection != websocket:
                await connection.send_text(message)

connection_manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    await connection_manager.connect(websocket)
    client = websocket.client.host
    print(f"{client} connected.")
    try:
        while(True):
            data = await websocket.receive_text()
            await connection_manager.send_personal_message(data, websocket)
            await connection_manager.broadcast(data, websocket)
    except WebSocketDisconnect:
        print(f"{client} disconnected.")

# --- DNS Service (registro de IPs) ---
DNS_LOG_FILE = "dns_log.txt"

@router.post("/dns/register")
async def register_dns(request: Request):
    client_ip = request.client.host
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Verificar si la IP ya ha sido registrada
    if os.path.exists(DNS_LOG_FILE):
        with open(DNS_LOG_FILE, "r") as f:
            logs = f.readlines()
        
        for log in logs:
            if client_ip in log:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={"message": "IP ya registrada previamente", "ip": client_ip, "timestamp": timestamp}
                )
            
    # Si no está registrada, registrar la IP
    with open(DNS_LOG_FILE, "a") as f:
        f.write(f"{timestamp} - {client_ip}\n")
    return {"message": "IP registrada", "ip": client_ip, "timestamp": timestamp}

@router.get("/dns/records")
async def list_dns_records():
    if not os.path.exists(DNS_LOG_FILE):
        return {"records": []}
    with open(DNS_LOG_FILE, "r") as f:
        lines = f.readlines()
    return {"records": [line.strip() for line in lines]}

# --- Streaming Service (audio/video) ---
STREAMING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "streaming")

# Asegúrate de que el directorio de streaming exista
os.makedirs(STREAMING_DIR, exist_ok=True)

# Función para obtener el tipo MIME según la extensión del archivo
def get_content_type(filename: str) -> str:
    extension = filename.split('.')[-1].lower()
    content_types = {
        # Video
        'mp4': 'video/mp4',
        'webm': 'video/webm',
        'avi': 'video/x-msvideo',
        'mov': 'video/quicktime',
        'mkv': 'video/x-matroska',
        # Audio
        'mp3': 'audio/mpeg',
        'ogg': 'audio/ogg',
        'wav': 'audio/wav',
        'aac': 'audio/aac',
        'flac': 'audio/flac'
    }
    return content_types.get(extension, 'application/octet-stream')

@router.get("/streaming/list")
async def list_streaming_files():
    if not os.path.exists(STREAMING_DIR):
        return {"files": []}
    files = [f for f in os.listdir(STREAMING_DIR) if os.path.isfile(os.path.join(STREAMING_DIR, f))]
    return {"files": files}

@router.post("/streaming/upload")
async def upload_streaming_file(file: UploadFile = File(...)):
    # Validación de tipos de archivo permitidos
    valid_extensions = ['mp4', 'webm', 'mp3', 'ogg', 'wav', 'aac', 'flac', 'avi', 'mov', 'mkv']
    file_ext = file.filename.split('.')[-1].lower()
    
    if file_ext not in valid_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de archivo no soportado. Formatos permitidos: {', '.join(valid_extensions)}"
        )
    
    # Guardar el archivo
    file_path = os.path.join(STREAMING_DIR, file.filename)
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            # Leer y escribir el archivo en chunks para evitar cargar todo en memoria
            while content := await file.read(1024 * 1024):  # Leer en chunks de 1MB
                await out_file.write(content)
        
        return {"message": "Archivo subido correctamente", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir el archivo: {str(e)}")

# Streaming con rangos de bytes (importante para que el navegador pueda buscar partes específicas del video/audio)
@router.get("/streaming/play/{filename}")
async def stream_media(filename: str, request: Request):
    file_path = os.path.join(STREAMING_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    file_size = os.path.getsize(file_path)
    content_type = get_content_type(filename)
    
    # Obtener el encabezado de rango del cliente (si está presente)
    range_header = request.headers.get("Range", "").strip()
    
    # Configuración predeterminada (enviar todo el archivo)
    status_code = 200
    headers = {
        "Content-Type": content_type,
        "Accept-Ranges": "bytes",
        "Content-Length": str(file_size)
    }
    
    # Si hay un encabezado de rango, procesar para streaming parcial
    if range_header:
        try:
            range_match = range_header.replace("bytes=", "").split("-")
            start_byte = int(range_match[0]) if range_match[0] else 0
            
            # Si el rango especifica un byte final, usarlo; de lo contrario, usar el tamaño del archivo - 1
            end_byte = int(range_match[1]) if range_match[1] else file_size - 1
            
            # Asegurarse de que end_byte no exceda el tamaño del archivo
            end_byte = min(end_byte, file_size - 1)
            
            # Calcular el tamaño del chunk a enviar
            chunk_size = end_byte - start_byte + 1
            
            # Configurar encabezados para respuesta parcial
            status_code = 206  # Partial Content
            headers["Content-Range"] = f"bytes {start_byte}-{end_byte}/{file_size}"
            headers["Content-Length"] = str(chunk_size)
            
        except (ValueError, IndexError):
            # Si hay un error en el encabezado de rango, ignorarlo y enviar el archivo completo
            start_byte = 0
            end_byte = file_size - 1
    else:
        # Sin encabezado de rango, enviar todo el archivo
        start_byte = 0
        end_byte = file_size - 1
    
    # Función generadora para streaming
    async def file_streamer():
        async with aiofiles.open(file_path, 'rb') as f:
            # Mover al inicio del rango solicitado
            await f.seek(start_byte)
            
            # Definir el tamaño de los chunks de lectura (1MB)
            chunk_size = 1024 * 1024
            bytes_to_read = end_byte - start_byte + 1
            
            # Leer y transmitir en chunks
            while bytes_to_read > 0:
                current_chunk_size = min(chunk_size, bytes_to_read)
                chunk = await f.read(current_chunk_size)
                if not chunk:
                    break
                    
                bytes_to_read -= len(chunk)
                yield chunk
                
                # Pequeña pausa para simular una transmisión más real
                # (puede eliminarse en producción)
                await asyncio.sleep(0.01)
    
    return StreamingResponse(
        content=file_streamer(),
        status_code=status_code,
        headers=headers
    )

# --- Streaming de cámara en vivo (simulado con WebSockets) ---
class VideoStreamManager:
    def __init__(self):
        self.active_streams = {}  # id_stream -> [lista de conexiones]
        self.broadcasters = {}    # id_stream -> websocket del broadcaster
    
    async def register_stream(self, stream_id: str, websocket: WebSocket):
        await websocket.accept()
        if stream_id not in self.active_streams:
            self.active_streams[stream_id] = []
        self.active_streams[stream_id].append(websocket)
    
    def remove_connection(self, stream_id: str, websocket: WebSocket):
        if stream_id in self.active_streams:
            if websocket in self.active_streams[stream_id]:
                self.active_streams[stream_id].remove(websocket)
            
            # Si no quedan conexiones, eliminar el stream
            if not self.active_streams[stream_id]:
                del self.active_streams[stream_id]
                
            # Si este era el broadcaster, eliminarlo
            if stream_id in self.broadcasters and self.broadcasters[stream_id] == websocket:
                del self.broadcasters[stream_id]
    
    async def broadcast_frame(self, stream_id: str, data: bytes, sender_ws: WebSocket):
        """Transmitir un frame a todos los espectadores del stream"""
        if stream_id in self.active_streams:
            disconnected = []
            
            for ws in self.active_streams[stream_id]:
                if ws != sender_ws:  # No enviar al emisor
                    try:
                        await ws.send_bytes(data)
                    except WebSocketDisconnect:
                        disconnected.append(ws)
            
            # Eliminar conexiones desconectadas
            for ws in disconnected:
                self.remove_connection(stream_id, ws)
    
    async def handle_json_message(self, stream_id: str, message: dict, sender_ws: WebSocket):
        """Manejar mensajes JSON entre participantes del stream"""
        message_type = message.get("type", "")
        
        if message_type == "broadcaster_connected":
            # Registrar este websocket como el broadcaster principal
            self.broadcasters[stream_id] = sender_ws
            print(f"Nuevo broadcaster registrado para stream {stream_id}")
            
            # Notificar al broadcaster cuántos espectadores hay conectados
            if stream_id in self.active_streams:
                viewer_count = len([ws for ws in self.active_streams[stream_id] if ws != sender_ws])
                if viewer_count > 0:
                    await sender_ws.send_json({
                        "type": "viewer_count",
                        "count": viewer_count
                    })
        
        elif message_type == "viewer_connected":
            # Notificar al broadcaster que un nuevo espectador se ha conectado
            if stream_id in self.broadcasters and self.broadcasters[stream_id] != sender_ws:
                try:
                    await self.broadcasters[stream_id].send_json({
                        "type": "viewer_connected"
                    })
                    print(f"Notificación enviada al broadcaster de stream {stream_id}")
                except Exception as e:
                    print(f"Error al notificar al broadcaster: {str(e)}")

video_stream_manager = VideoStreamManager()

@router.websocket("/ws/stream/{stream_id}")
async def websocket_stream(websocket: WebSocket, stream_id: str):
    # Registrar la conexión en el gestor de streams
    try:
        print(f"Nueva conexión WebSocket para stream {stream_id}")
        await video_stream_manager.register_stream(stream_id, websocket)
        
        # Enviar mensaje de confirmación de conexión
        await websocket.send_json({
            "type": "connection_established",
            "stream_id": stream_id,
            "status": "connected"
        })
        
        while True:
            try:
                # Primero intentar recibir datos binarios (frames)
                data = await websocket.receive_bytes()
                data_size = len(data)
                # print(f"Datos binarios recibidos para stream {stream_id}: {data_size} bytes")
                
                # Transmitir a todos los conectados a este stream
                await video_stream_manager.broadcast_frame(stream_id, data, websocket)
            except Exception as bin_err:
                if not isinstance(bin_err, WebSocketDisconnect):
                    try:
                        # Si no son datos binarios, intentar recibir texto
                        message = await websocket.receive_text()
                        try:
                            json_message = json.loads(message)
                            await video_stream_manager.handle_json_message(stream_id, json_message, websocket)
                        except json.JSONDecodeError:
                            # Ignorar silenciosamente mensajes de texto no-JSON
                            pass
                    except WebSocketDisconnect as e:
                        print(f"WebSocket desconectado para stream {stream_id}, código: {e.code}")
                        video_stream_manager.remove_connection(stream_id, websocket)
                        return
                    except Exception:
                        # Ignorar otros errores en la recepción de mensajes
                        pass
                else:
                    # Es un WebSocketDisconnect, salir del bucle
                    print(f"WebSocket desconectado (binario) para stream {stream_id}, código: {bin_err.code}")
                    video_stream_manager.remove_connection(stream_id, websocket)
                    return
            
    except WebSocketDisconnect as e:
        # Eliminar la conexión cuando se desconecte
        print(f"WebSocket desconectado para stream {stream_id}, código: {e.code}")
        video_stream_manager.remove_connection(stream_id, websocket)
    except Exception as e:
        print(f"Error no esperado en WebSocket para stream {stream_id}: {str(e)}")
        try:
            video_stream_manager.remove_connection(stream_id, websocket)
        except:
            pass

# --- FTP Download ---
@router.get("/ftp/download/{filename}")
async def download_ftp_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(file_path, filename=filename)

# --- Mail Inbox (recepción desde archivos planos simulando bandeja local) ---
MAILBOX_DIR = "mailbox"
os.makedirs(MAILBOX_DIR, exist_ok=True)

@router.get("/mail/inbox")
async def list_mail():
    mails = []
    for fname in os.listdir(MAILBOX_DIR):
        path = os.path.join(MAILBOX_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        mails.append({"filename": fname, "content": content})
    return {"inbox": mails}