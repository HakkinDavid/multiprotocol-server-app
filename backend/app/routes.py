import os
import shutil
import asyncio
import smtplib
from email.mime.text import MIMEText
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, WebSocket, WebSocketDisconnect, Request

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.auth import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user

from fastapi.responses import FileResponse, StreamingResponse
import time


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
    try:
        while(True):
            data = await websocket.receive_text()
            await connection_manager.send_personal_message(data, websocket)
            await connection_manager.broadcast(data, websocket)
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        await connection_manager.broadcast(f"{client} left the chat")

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
STREAMING_DIR = "streaming"

@router.get("/streaming/list")
async def list_streaming_files():
    if not os.path.exists(STREAMING_DIR):
        return {"files": []}
    return {"files": os.listdir(STREAMING_DIR)}

@router.get("/streaming/play/{filename}")
async def stream_media(filename: str):
    file_path = os.path.join(STREAMING_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    def file_iterator():
        with open(file_path, "rb") as f:
            yield from f

    media_type = "video/mp4" if filename.endswith(".mp4") else "audio/mpeg"
    return StreamingResponse(file_iterator(), media_type=media_type)

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