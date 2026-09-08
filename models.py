from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Restaurante(Base):
    __tablename__ = "restaurantes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    ciudad = Column(String, index=True, nullable=False)
    estado = Column(String, index=True, nullable=False)
    tipo_cocina = Column(String, index=True)  # Ej. Mexicana, Italiana, Mariscos
    activo = Column(Boolean, default=True)   # Para controlar si pagaron su membresía SaaS

    # 🔗 Relaciones: Un restaurante tiene muchas mesas y muchas reservas
    mesas = relationship("Mesa", back_populates="restaurante", cascade="all, delete-orphan")
    reservas = relationship("Reserva", back_populates="restaurante", cascade="all, delete-orphan")


class Mesa(Base):
    __tablename__ = "mesas"

    id = Column(Integer, primary_key=True, index=True)
    restaurante_id = Column(Integer, ForeignKey("restaurantes.id"), nullable=False)
    numero_mesa = Column(String, nullable=False)  # Ej. "Mesa 1", "VIP 2"
    zona = Column(String, default="Salón")        # Ej. Terraza, Salón, Barra
    capacidad_max = Column(Integer, nullable=False)  # Cantidad máxima de comensales

    # 🔗 Relaciones
    restaurante = relationship("Restaurante", back_populates="mesas")
    reservas = relationship("Reserva", back_populates="mesa")


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
    correo = Column(String, unique=True, index=True, nullable=False)

    # 🔗 Relaciones
    reservas = relationship("Reserva", back_populates="cliente")


class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    restaurante_id = Column(Integer, ForeignKey("restaurantes.id"), nullable=False)
    mesa_id = Column(Integer, ForeignKey("mesas.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    num_comensales = Column(Integer, nullable=False)
    status = Column(String, default="Confirmada")  # Confirmada, Cancelada, Asistió

    # 🔗 Relaciones cruzadas para consultar la información de golpe
    restaurante = relationship("Restaurante", back_populates="reservas")
    mesa = relationship("Mesa", back_populates="reservas")
    cliente = relationship("Cliente", back_populates="reservas")
    