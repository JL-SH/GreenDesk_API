import time
from fastapi import FastAPI, Request
from app.api.routes import users, devices, generic

app = FastAPI(
    title="GreenDesk Inventory API",
    description="API profesional para gestión de activos con Auditoría JSONB y Migraciones",
    version="1.0.0"
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.include_router(users.router)
app.include_router(devices.router)
app.include_router(generic.router)
