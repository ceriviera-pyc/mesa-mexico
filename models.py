from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, Boolean, DateTime
from sqlalchemy.orm import relationship
from database import Base

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

    # Relaciones
    restaurante = relationship("Restaurante", back_populates="reservas")
    mesa = relationship("Mesa", back_populates="reservas")
    cliente = relationship("Cliente", back_populates="reservas")
