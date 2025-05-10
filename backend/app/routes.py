import os
import shutil
import asyncio
import smtplib
from email.mime.text import MIMEText

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.auth import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user

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

# --- DNS Service ---
# In-memory storage for DNS records.
dns_records = []

@router.post("/dns/register")
async def register_dns(name: str, ip: str):
    # Automatically generate a DNS record for a new machine interacting via the API
    dns_record = {
        "name": name,
        "type": "A",
        "value": ip
    }
    dns_records.append(dns_record)
    return {"message": "DNS record created", "record": dns_record}

@router.get("/dns/records")
async def get_dns_records():
    return {"records": dns_records}

@router.post("/dns/records")
async def add_dns_record(record: dict):
    required_keys = {"name", "type", "value"}
    if not required_keys.issubset(record.keys()):
        raise HTTPException(status_code=400, detail="Missing required DNS record fields")
    dns_records.append(record)
    return {"message": "DNS record added", "record": record}

@router.post("/dns/auto")
async def auto_create_dns(record: dict):
    # Expected fields: machine_name and ip_address
    if not all(k in record for k in ("machine_name", "ip_address")):
         raise HTTPException(status_code=400, detail="Missing required fields: machine_name and ip_address")
    new_record = {"name": f"{record['machine_name']}", "type": "A", "value": record["ip_address"]}
    dns_records.append(new_record)
    return {"message": "DNS record automatically created", "record": new_record}

# --- Web Service ---
WEB_CONTENT_FILE = "web_content.html"

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

# --- Streaming Service ---
streaming_status = {"status": "stopped"}

@router.get("/streaming/status")
async def get_streaming_status():
    return streaming_status

@router.post("/streaming/start")
async def start_streaming():
    streaming_status["status"] = "started"
    asyncio.create_task(simulate_streaming())
    return {"message": "Streaming started"}

@router.post("/streaming/stop")
async def stop_streaming():
    streaming_status["status"] = "stopped"
    return {"message": "Streaming stopped"}

async def simulate_streaming():
    await asyncio.sleep(60)
    streaming_status["status"] = "stopped"

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

# --- DNS Service ---
# Updated DNS implementation in routes.py

# Store DNS records in memory with timestamp and last connected info
dns_records = []

@router.post("/dns/register")
async def register_dns(record: dict):
    """Register a DNS record with name and IP"""
    if "name" not in record or "ip" not in record:
        raise HTTPException(status_code=400, detail="Missing required fields: name and ip")
    
    # Check if record already exists and update it
    for i, existing in enumerate(dns_records):
        if existing["name"] == record["name"]:
            dns_records[i] = {
                "name": record["name"],
                "type": "A",
                "value": record["ip"],
                "last_connected": datetime.datetime.now().isoformat()
            }
            return {"message": "DNS record updated", "record": dns_records[i]}
    
    # Add new record
    new_record = {
        "name": record["name"],
        "type": "A", 
        "value": record["ip"],
        "last_connected": datetime.datetime.now().isoformat()
    }
    dns_records.append(new_record)
    return {"message": "DNS record created", "record": new_record}

@router.get("/dns/records")
async def get_dns_records():
    """Get all DNS records"""
    return {"records": dns_records}

@router.post("/dns/auto")
async def auto_create_dns(request: Request):
    """Automatically register client IP"""
    client_host = request.client.host
    # Generate a unique name based on client IP with timestamp
    machine_name = f"client-{client_host.replace('.', '-')}"
    
    # Register the DNS record
    record = {
        "name": machine_name,
        "ip": client_host,
    }
    
    result = await register_dns(record)
    return result

@router.delete("/dns/records/{name}")
async def delete_dns_record(name: str):
    """Delete a DNS record by name"""
    for i, record in enumerate(dns_records):
        if record["name"] == name:
            deleted = dns_records.pop(i)
            return {"message": f"DNS record {name} deleted", "record": deleted}
    
    raise HTTPException(status_code=404, detail=f"DNS record {name} not found")

# --- Streaming Service ---
import os
from typing import List
from fastapi import Header, HTTPException, Response
from fastapi.responses import StreamingResponse

# Directory for stream files
STREAMING_DIR = "streaming"
if not os.path.exists(STREAMING_DIR):
    os.makedirs(STREAMING_DIR)

# In-memory streaming status
streaming_status = {"status": "stopped", "current_file": None}

@router.get("/streaming/status")
async def get_streaming_status():
    """Get current streaming status"""
    return streaming_status

@router.post("/streaming/start")
async def start_streaming(file_name: str = None):
    """Start streaming a specific file"""
    if file_name:
        file_path = os.path.join(STREAMING_DIR, file_name)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File {file_name} not found")
        
        streaming_status["status"] = "started"
        streaming_status["current_file"] = file_name
        return {"message": f"Streaming {file_name} started", "status": "started"}
    else:
        raise HTTPException(status_code=400, detail="File name is required")

@router.post("/streaming/stop")
async def stop_streaming():
    """Stop current streaming"""
    streaming_status["status"] = "stopped"
    streaming_status["current_file"] = None
    return {"message": "Streaming stopped", "status": "stopped"}

@router.get("/streaming/files")
async def list_streaming_files():
    """List available streaming files"""
    files = []
    
    if os.path.exists(STREAMING_DIR):
        for file in os.listdir(STREAMING_DIR):
            file_path = os.path.join(STREAMING_DIR, file)
            if os.path.isfile(file_path):
                # Get file extension and determine type
                _, ext = os.path.splitext(file)
                file_type = "unknown"
                if ext.lower() in ['.mp4', '.webm', '.ogg', '.mov']:
                    file_type = "video"
                elif ext.lower() in ['.mp3', '.wav', '.ogg', '.flac']:
                    file_type = "audio"
                
                files.append({
                    "name": file,
                    "type": file_type,
                    "size": os.path.getsize(file_path),
                    "created": os.path.getctime(file_path)
                })
    
    return {"files": files}

@router.post("/streaming/upload")
async def upload_streaming_file(file: UploadFile = File(...)):
    """Upload a file for streaming"""
    # Save the file to the streaming directory
    file_location = os.path.join(STREAMING_DIR, file.filename)
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    return {"message": "Streaming file uploaded", "filename": file.filename}

@router.get("/streaming/play/{file_name}")
async def stream_file(file_name: str, range: str = Header(None)):
    """Stream a file with support for Range requests (for HTML5 video/audio)"""
    file_path = os.path.join(STREAMING_DIR, file_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File {file_name} not found")
    
    file_size = os.path.getsize(file_path)
    
    # Determine content type based on file extension
    _, ext = os.path.splitext(file_name)
    content_type = "application/octet-stream"  # Default
    
    if ext.lower() in ['.mp4', '.mov']:
        content_type = "video/mp4"
    elif ext.lower() == '.webm':
        content_type = "video/webm"
    elif ext.lower() == '.mp3':
        content_type = "audio/mpeg"
    elif ext.lower() == '.wav':
        content_type = "audio/wav"
    elif ext.lower() == '.ogg':
        # Could be audio or video
        content_type = "application/ogg"
    elif ext.lower() == '.flac':
        content_type = "audio/flac"
    
    # Handle range request (for browsers seeking in video/audio)
    start = 0
    end = file_size - 1
    
    if range:
        try:
            # Parse Range header
            range_str = range.replace("bytes=", "")
            start, end = range_str.split("-")
            start = int(start)
            if end:
                end = int(end)
            else:
                end = file_size - 1
        except ValueError:
            # Invalid range header, use default range
            pass
    
    # Ensure we don't go beyond file size
    end = min(end, file_size - 1)
    content_length = end - start + 1
    
    # Create and return streaming response
    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(content_length),
        "Content-Type": content_type,
    }
    
    async def file_iterator():
        with open(file_path, "rb") as f:
            f.seek(start)
            data = f.read(min(content_length, 1024 * 1024))  # Read in 1MB chunks
            while data:
                yield data
                data = f.read(min(content_length - f.tell() + start, 1024 * 1024))
    
    return StreamingResponse(
        file_iterator(),
        status_code=206 if range else 200,
        headers=headers
    )