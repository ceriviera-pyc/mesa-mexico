from pydantic import BaseModel
from typing import Optional

# 🏢 Estructura base que define qué datos son obligatorios para registrar un restaurante
class RestauranteCreate(BaseModel):
    nombre: str
    ciudad: str
    estado: str
    tipo_cocina: Optional[str] = "Mexicana"
 
# 👥 Estructura obligatoria para registrar un cliente en la plataforma nacional
class ClienteCreate(BaseModel):
    nombre: str
    telefono: str
    correo: str   
 
 
# 📅 Estructura obligatoria para solicitar una reserva en la plataforma
class ReservaCreate(BaseModel):
    restaurante_id: int
    cliente_id: int
    fecha: str  # Formato esperado: YYYY-MM-DD (Ej. 2026-09-15)
    hora: str   # Formato esperado: HH:MM (Ej. 20:00)
    num_comensales: int    
  
  
# 🔄 Estructura para actualizar únicamente el estado de una reservación
class ReservaStatusUpdate(BaseModel):
    status: str  # Valores esperados: "Confirmada", "Asistió", "Cancelada"    