from pydantic import BaseModel
from typing import Optional, List

# 🏢 1. Moldes para que las empresas den de alta sus restaurantes reales
class RestauranteCreate(BaseModel):
    nombre: str
    ciudad: str
    estado: str
    tipo_cocina: Optional[str] = "Mexicana"
    imagen_url: Optional[str] = "/static/imagenes/defecto.jpg"
    sitio_web: Optional[str] = None

# 👥 2. Datos obligatorios para el Registro Inicial (Comensal o Locales)
class ClienteCreate(BaseModel):
    nombre: str
    telefono: str
    correo: str  # ⚡ Cambiado a str plano para resolver el problema de email-validator
    password: str
    rol: Optional[str] = "cliente"  # Puede recibir 'cliente' o 'empresa'

# ✉️ 3. Datos para validar el PIN de activación inalámbrica
class VerificarRegistro(BaseModel):
    correo: str
    codigo: str

# 🔑 4. Datos para el Login Diario Tradicional
class ClienteLogin(BaseModel):
    correo: str  # ⚡ Cambiado a str plano para evitar trabas del servidor local
    password: str

class ClienteResponse(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: str

    class Config:
        from_attributes = True

# 📅 5. Estructura para solicitar una reserva en la plataforma
class ReservaCreate(BaseModel):
    restaurante_id: int
    cliente_id: int
    fecha: str  # Formato: YYYY-MM-DD
    hora: str   # Formato: HH:MM
    num_comensales: int    

# 🔄 6. Estructura para actualizar el estado de una reservación
class ReservaStatusUpdate(BaseModel):
    status: str  # "Confirmada", "Asistió", "Cancelada"
