from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, Boolean, DateTime, Float  # 👈 Se agregó Float aquí
from sqlalchemy.orm import relationship
from database import Base
import datetime as dt 

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
    correo = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    
    # 💼 ROL DEL USUARIO: 'cliente' (comensal ordinario) o 'empresa' (dueño de restaurante)
    rol = Column(String, default="cliente", nullable=False)
    
    # 🔐 Campos de control de seguridad
    verificado = Column(Boolean, default=False)
    codigo_verificacion = Column(String, nullable=True)
    codigo_expiracion = Column(DateTime, nullable=True)

    # 🗺️ Coordenadas del Comensal (Ubicación en tiempo real)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)

    # Relaciones
    reservas = relationship("Reserva", back_populates="cliente")
    restaurantes_propios = relationship("Restaurante", back_populates="dueno")

class Restaurante(Base):
    __tablename__ = "restaurantes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    ciudad = Column(String, index=True, nullable=False)
    estado = Column(String, index=True, nullable=False)
    tipo_cocina = Column(String, index=True)
    activo = Column(Boolean, default=True)
    
    # 🖼️ Campos multimedia premium
    imagen_url = Column(String, default="/static/imagenes/defecto.jpg")
    sitio_web = Column(String, nullable=True)

    # 🔗 ENLACE EMPRESARIAL: ID de la empresa/dueño que administra el local
    dueno_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)

    # 🗺️ Coordenadas Físicas del Establecimiento (AGREGA ESTAS DOS LÍNEAS AQUÍ)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    
    # ⏰ Horarios de operación comercial
    hora_apertura = Column(String, default="13:00")  # Abre a la 1:00 PM por defecto
    hora_cierre = Column(String, default="23:00")    # Cierra a las 11:00 PM por defecto
    intervalo_bloque = Column(Integer, default=30)   # Genera bloques cada 30 minutos

    # Relaciones
    dueno = relationship("Cliente", back_populates="restaurantes_propios")
    mesas = relationship("Mesa", back_populates="restaurante", cascade="all, delete-orphan")
    reservas = relationship("Reserva", back_populates="restaurante", cascade="all, delete-orphan")


class Mesa(Base):
    __tablename__ = "mesas"

    id = Column(Integer, primary_key=True, index=True)
    restaurante_id = Column(Integer, ForeignKey("restaurantes.id"), nullable=False)
    numero_mesa = Column(String, nullable=False)
    zona = Column(String, default="Salón")
    capacidad_max = Column(Integer, nullable=False)

    # Relaciones
    restaurante = relationship("Restaurante", back_populates="mesas")
    reservas = relationship("Reserva", back_populates="mesa")


class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    restaurante_id = Column(Integer, ForeignKey("restaurantes.id"), nullable=False)
    mesa_id = Column(Integer, ForeignKey("mesas.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    num_comensales = Column(Integer, nullable=False)
    status = Column(String, default="Confirmada")
    # 📝 1. NOTAS DEL CLIENTE (El corazón del CRM)
    # Permite al usuario avisar si es un aniversario, si prefiere terraza o si hay alergias.
    notas = Column(String, nullable=True)
    # ⏳ 2. CONTROL DE TIEMPO AUTOMÁTICO (Auditoría interna)
    # Guarda el milisegundo exacto en que se creó la reserva para saber cuándo se agendó.
    creado_en = Column(DateTime, default=dt.datetime.utcnow)
    # 🔄 3. HISTORIAL DE CAMBIOS
    # Registra cuándo se modificó el estatus o el horario por última vez.
    actualizado_en = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)
    # Relaciones
    restaurante = relationship("Restaurante", back_populates="reservas")
    mesa = relationship("Mesa", back_populates="reservas")
    cliente = relationship("Cliente", back_populates="reservas")
