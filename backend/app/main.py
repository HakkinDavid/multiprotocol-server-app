from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from app.routes import router  # Tu archivo de rutas
from app.database import get_db
import os

app = FastAPI()

# Permitir acceso desde SvelteKit (ajustar para producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajustar para tu dominio de frontend en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/dns/status")
async def dns_status():
    # Lógica de DNS
    return {"service": "DNS", "status": "running"}


@app.post("/dns/configure")
async def configure_dns(settings: dict):
    # Configura el servidor DNS con los valores proporcionados
    # Implementar la lógica para configurar DNS en base a la configuración dada
    try:
        pass  # Lógica de configuración del servicio DNS aquí
        return {"service": "DNS", "status": "configured", "settings": settings}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error de configuración DNS: {str(e)}")


@app.get("/web/status")
async def web_status():
    # Lógica del estado del servidor web
    return {"service": "Web", "status": "running"}


@app.get("/streaming/status")
async def streaming_status():
    # Lógica del estado del servidor de streaming
    return {"service": "Streaming", "status": "running"}


@app.post("/streaming/start")
async def start_streaming():
    # Implementa la lógica para iniciar streaming
    try:
        pass  # Lógica de inicio de transmisión de video/audio aquí
        return {"service": "Streaming", "status": "started"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al iniciar streaming: {str(e)}")


@app.get("/mail/status")
async def mail_status():
    # Lógica del estado del servidor de correo
    return {"service": "Mail", "status": "running"}


@app.post("/mail/send")
async def send_mail(mail_data: dict):
    # Lógica para enviar un correo electrónico
    try:
        pass  # Lógica para el envío del correo aquí
        return {"service": "Mail", "status": "sent", "details": mail_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al enviar correo: {str(e)}")


@app.get("/ftp/status")
async def ftp_status():
    # Lógica del estado del servidor FTP
    return {"service": "FTP", "status": "running"}


@app.post("/ftp/upload")
async def upload_ftp(file_data: dict):
    # Lógica para cargar archivos al servidor FTP
    try:
        # Supón la lógica para manejar archivos
        file_path = "uploads/" + file_data['filename']
        print(file_path)
        with open(file_path, "wb") as f:
            f.write(file_data['content'])  # Solo ejemplo, debe manejar uploads correctamente
        return {"service": "FTP", "status": "uploaded", "file": file_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al subir archivo FTP: {str(e)}")


# Endpoints de prueba para búsqueda general
@app.get("/")
async def root():
    return {"message": "Multiprotocol Server - Services enabled for DNS, Web, Streaming, Mail & FTP"}