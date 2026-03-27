from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, guests, reservations, rooms, ws


app = FastAPI(title="Gestión hotelera API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://localhost:5001", "http://fe:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(guests.router)
app.include_router(reservations.router)
app.include_router(ws.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
