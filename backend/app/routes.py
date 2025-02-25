import os
import shutil
import asyncio
import smtplib
from email.mime.text import MIMEText

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
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
