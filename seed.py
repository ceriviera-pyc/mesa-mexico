import models
from database import SessionLocal, engine

# Aseguramos que las tablas se borren y se vuelvan a crear con las nuevas columnas
models.Base.metadata.drop_all(bind=engine)   # 👈 AGREGA ESTA LÍNEA AQUÍ
models.Base.metadata.create_all(bind=engine)


def alimentar_base_datos():
    db = SessionLocal()
    try:
        # 🏢 1. Limpiamos datos anteriores para evitar duplicados al hacer pruebas
        db.query(models.Reserva).delete()
        db.query(models.Cliente).delete()
        db.query(models.Mesa).delete()
        db.query(models.Restaurante).delete()
        db.commit()
        print("🧹 Base de datos local limpia y lista.")

        # 🇲🇽 2. Creación de Restaurantes Piloto en México con Datos Corporativos Premium
        restaurante1 = models.Restaurante(
            nombre="Mariscos Riviera", 
            ciudad="Playa del Carmen", 
            estado="Quintana Roo", 
            tipo_cocina="Mariscos",
            imagen_url="https://unsplash.com",
            sitio_web="https://google.com"
        )
        restaurante2 = models.Restaurante(
            nombre="El Asador del Centro", 
            ciudad="Ciudad de México", 
            estado="CDMX", 
            tipo_cocina="Cortes de Carne",
            imagen_url="https://unsplash.com",
            sitio_web="https://google.com"
        )
        restaurante3 = models.Restaurante(
            nombre="La Cantina de Guadalajara", 
            ciudad="Guadalajara", 
            estado="Jalisco", 
            tipo_cocina="Mexicana Tradicional",
            imagen_url="https://unsplash.com",
            sitio_web="https://google.com"
        )

        db.add_all([restaurante1, restaurante2, restaurante3])
        db.commit()
        

        # 🪑 3. Creación de Mesas por Zonas y Capacidades
        # Mesas para Mariscos Riviera (Playa del Carmen)
        mesas_riviera = [
            models.Mesa(restaurante_id=restaurante1.id, numero_mesa="Terraza 1", zona="Terraza", capacidad_max=4),
            models.Mesa(restaurante_id=restaurante1.id, numero_mesa="Terraza 2", zona="Terraza", capacidad_max=2),
            models.Mesa(restaurante_id=restaurante1.id, numero_mesa="Mesa Interior 3", zona="Salón", capacidad_max=6),
            models.Mesa(restaurante_id=restaurante1.id, numero_mesa="Mesa Interior 4", zona="Salón", capacidad_max=4),
            models.Mesa(restaurante_id=restaurante1.id, numero_mesa="Barra 5", zona="Barra", capacidad_max=2),
        ]

        # Mesas para El Asador del Centro (CDMX)
        mesas_asador = [
            models.Mesa(restaurante_id=restaurante2.id, numero_mesa="Mesa 101", zona="Salón Principal", capacidad_max=4),
            models.Mesa(restaurante_id=restaurante2.id, numero_mesa="Mesa 102", zona="Salón Principal", capacidad_max=4),
            models.Mesa(restaurante_id=restaurante2.id, numero_mesa="VIP 1", zona="Privado", capacidad_max=8),
            models.Mesa(restaurante_id=restaurante2.id, numero_mesa="VIP 2", zona="Privado", capacidad_max=10),
        ]

        # Mesas para La Cantina de Guadalajara (Jalisco)
        mesas_cantina = [
            models.Mesa(restaurante_id=restaurante3.id, numero_mesa="Patio 1", zona="Patio", capacidad_max=4),
            models.Mesa(restaurante_id=restaurante3.id, numero_mesa="Patio 2", zona="Patio", capacidad_max=6),
            models.Mesa(restaurante_id=restaurante3.id, numero_mesa="Mesa Centro 3", zona="Salón", capacidad_max=4),
        ]

        db.add_all(mesas_riviera + mesas_asador + mesas_cantina)
        db.commit()
        print("✅ ÉXITO: Restaurantes y mesas de prueba inyectados correctamente en 'mesa_mexico.db'.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error al alimentar la base de datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    alimentar_base_datos()
    