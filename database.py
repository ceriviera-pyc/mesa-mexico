import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 📂 Definimos la ruta física donde se guardará la base de datos local
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'mesa_mexico.db')}"

# 🔌 Creamos el motor de conexión (engine)
# El argumento 'check_same_thread' es exclusivo y necesario para que SQLite trabaje con FastAPI
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 🗄️ Creamos la fábrica de sesiones para interactuar con las tablas
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 🧱 Definimos la Clase Base de la cual heredarán todas nuestras tablas maestras
Base = declarative_base()

# 💧 Función utilitaria para abrir y cerrar la base de datos de forma segura en cada petición
def obtener_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()