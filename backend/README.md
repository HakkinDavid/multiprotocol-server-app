# Backend - FastAPI

This backend is developed using FastApi to manage the services of the application.

## Instalation

1. Clone the repository (if you haven't) and move into the backend directory
```
git clone https://github.com/HakkinDavid/multiprotocol-server-app
cd backend
```
2. Create and activate a virtual environment for python
```
python -m venv venv
source venv/bin/activate  # On Linux/macOS
venv\Scripts\activate     # On Windows
```
3. Install dependencies
```
pip install "fastapi[standard]"
```

## Run the server
```
fastapi dev main.py  
```