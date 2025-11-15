# main.py - Microservicio de EDICIÓN (UPDATE)
import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "caballerosdb")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "caballeros")

if not MONGO_URI:
    raise RuntimeError("La variable de entorno MONGO_URI no está configurada")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
caballeros_col = db[MONGO_COLLECTION]

app = FastAPI(title="MS Edición Caballeros")

# ====== CORS ======
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],   # IMPORTANTE: incluye PUT
    allow_headers=["*"],
)

class CaballeroUpdate(BaseModel):
    nombre: Optional[str] = None
    constelacion: Optional[str] = None
    edad: Optional[int] = None
    urlImagen: Optional[str] = None
    altura: Optional[float] = None
    class Config:
        # Ignora cualquier campo extra que llegue en el body
        extra = "ignore"


@app.get("/")
def raiz():
    return {"mensaje": "MS Edición Caballeros funcionando"}


@app.put("/caballeros/{id}")
def editar_caballero(id: str, datos: CaballeroUpdate):
    """
    PUT /caballeros/{id}
    Body: campos a actualizar (parcial)
    """
    # Validar ID
    try:
        oid = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")

    # Convertir solo los campos no nulos a dict
    cambios = {k: v for k, v in datos.dict().items() if v is not None}

    if not cambios:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")

    result = caballeros_col.update_one({"_id": oid}, {"$set": cambios})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Caballero no encontrado")

    return {
        "ok": True,
        "mensaje": "Caballero actualizado correctamente",
        "cambios": cambios,
    }
