from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
import models
import schemas
from database import engine, obtener_db

# Fabricamos las tablas físicas en el disco duro si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mesa México Oficial- Plataforma Multinegocio de Reservas",
    version="1.0.0"
)

@app.get("/")
def leer_raiz():
    return {
        "status": "success",
        "mensaje": "Bienvenido al motor central de Mesa México. Servidor local operando al 100%."
    }

# 🔍 RUTA DE CONSULTA: Listar los restaurantes registrados
@app.get("/restaurantes")
def listar_restaurantes(db: Session = Depends(obtener_db)):
    restaurantes = db.query(models.Restaurante).all()
    return {"total": len(restaurantes), "data": restaurantes}


# 📝 RUTA DE REGISTRO (POST): Formulario para dar de alta un restaurante nuevo en México
@app.post("/restaurantes")
def crear_restaurante(restaurante: schemas.RestauranteCreate, db: Session = Depends(obtener_db)):
    # Creamos la entidad mapeada con la base de datos usando los datos del formulario
    nuevo_negocio = models.Restaurante(
        nombre=restaurante.nombre,
        ciudad=restaurante.ciudad,
        estado=restaurante.estado,
        tipo_cocina=restaurante.tipo_cocina
    )
    
    db.add(nuevo_negocio)
    db.commit()          # Guardamos físicamente en la base de datos
    db.refresh(nuevo_negocio)  # Refrescamos para obtener el ID único asignado por SQL
    
    return {
        "status": "success",
        "mensaje": f"¡Éxito! El restaurante '{nuevo_negocio.nombre}' ha sido registrado en {nuevo_negocio.ciudad} con el ID {nuevo_negocio.id}.",
        "data": nuevo_negocio
    }
    
    

# 🔍 RUTA DE CONSULTA: Listar todos los clientes registrados en la plataforma
@app.get("/clientes")
def listar_clientes(db: Session = Depends(obtener_db)):
    clientes = db.query(models.Cliente).all()
    return {"total": len(clientes), "data": clientes}


# 👤 RUTA DE REGISTRO (POST): Dar de alta un comensal nuevo en el sistema
@app.post("/clientes")
def crear_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(obtener_db)):
    # 🕵️‍♂️ Validación crucial: Verificar si el correo ya existe en el sistema nacional
    correo_existe = db.query(models.Cliente).filter(models.Cliente.correo == cliente.correo).first()
    if correo_existe:
        raise HTTPException(
            status_code=400, 
            detail="🚫 ERROR: Este correo electrónico ya está registrado con otro cliente en México."
        )
        
    nuevo_cliente = models.Cliente(
        nombre=cliente.nombre,
        telefono=cliente.telefono,
        correo=cliente.correo.lower().strip()
    )
    
    db.add(nuevo_cliente)
    db.commit()          # Guardamos físicamente en la base de datos mesa_mexico.db
    db.refresh(nuevo_cliente)
    
    return {
        "status": "success",
        "mensaje": f"¡Éxito! El cliente '{nuevo_cliente.nombre}' ha sido registrado exitosamente con el ID {nuevo_cliente.id}.",
        "data": nuevo_cliente
    }


from datetime import datetime

# 🔍 RUTA DE CONSULTA: Ver el historial global de reservas en México
@app.get("/reservas")
def listar_reservas(db: Session = Depends(obtener_db)):
    reservas = db.query(models.Reserva).all()
    return {"total": len(reservas), "data": reservas}


# 📅 RUTA DE RESERVA (POST): El motor inteligente que busca mesa libre y bloquea el horario
@app.post("/reservas")
def crear_reserva(reserva: schemas.ReservaCreate, db: Session = Depends(obtener_db)):
    try:
        # Convertimos los textos de fecha y hora en objetos reales de tiempo de Python
        fecha_obj = datetime.strptime(reserva.fecha, "%Y-%m-%d").date()
        hora_obj = datetime.strptime(reserva.hora, "%H:%M").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="🚫 Formato incorrecto. Use Fecha: YYYY-MM-DD y Hora: HH:MM")

    # 1. Buscar todas las mesas de ese restaurante específico que aguanten a los comensales
    mesas_candidatas = db.query(models.Mesa).filter(
        models.Mesa.restaurante_id == reserva.restaurante_id,
        models.Mesa.capacidad_max >= reserva.num_comensales
    ).all()

    if not mesas_candidatas:
        raise HTTPException(status_code=404, detail="🚫 Lo sentimos, el restaurante no tiene mesas con esa capacidad.")

    # 2. El algoritmo busca cuál de esas mesas está libre en el horario solicitado
    mesa_asignada = None
    for mesa in mesas_candidatas:
        # Buscamos si esta mesa en específico ya tiene una reserva activa que choque a esa hora
        choque = db.query(models.Reserva).filter(
            models.Reserva.mesa_id == mesa.id,
            models.Reserva.fecha == fecha_obj,
            models.Reserva.hora == hora_obj,
            models.Reserva.status == "Confirmada"
        ).first()
        
        # ¡Si no hay choque, encontramos la mesa perfecta!
        if not choque:
            mesa_asignada = mesa
            break

    # 3. Si el ciclo terminó y no encontramos ninguna mesa libre, detenemos el proceso
    if not mesa_asignada:
        raise HTTPException(
            status_code=400, 
            detail="🚫 COMPLETO: No hay mesas disponibles para esa cantidad de personas en la fecha y hora seleccionadas."
        )

    # 4. Si hay mesa libre, el sistema la aparta físicamente en la base de datos
    nueva_reserva = models.Reserva(
        restaurante_id=reserva.restaurante_id,
        mesa_id=mesa_asignada.id,
        cliente_id=reserva.cliente_id,
        fecha=fecha_obj,
        hora=hora_obj,
        num_comensales=reserva.num_comensales
    )

    db.add(nueva_reserva)
    db.commit()  # Guardamos el candado físico en mesa_mexico.db
    db.refresh(nueva_reserva)

    return {
        "status": "success",
        "mensaje": f"¡RESERVA CONFIRMADA EXITOSAMENTE! Se le ha asignado la '{mesa_asignada.numero_mesa}' en la zona '{mesa_asignada.zona}'.",
        "detalles": {
            "reserva_id": nueva_reserva.id,
            "restaurante_id": nueva_reserva.restaurante_id,
            "mesa": mesa_asignada.numero_mesa,
            "zona": mesa_asignada.zona,
            "fecha": str(nueva_reserva.fecha),
            "hora": str(nueva_reserva.hora)
        }
    }       


# 🔍 MOTOR DE BÚSQUEDA AVANZADO: Filtrar restaurantes con mesas libres por Ciudad y Capacidad
@app.get("/buscar")
def buscar_disponibilidad_ciudad(ciudad: str, personas: int, db: Session = Depends(obtener_db)):
    # 1. Buscamos todos los restaurantes que estén en la ciudad solicitada y activos
    restaurantes_locales = db.query(models.Restaurante).filter(
        models.Restaurante.ciudad.like(f"%{ciudad.strip()}%"),
        models.Restaurante.activo == True
    ).all()

    if not restaurantes_locales:
        return {
            "status": "success",
            "mensaje": f"Por el momento no hay restaurantes registrados en la ciudad de '{ciudad}'.",
            "data": []
        }

    resultado_busqueda = []

    # 2. Analizamos restaurante por restaurante para ver si tienen mesas que aguanten al grupo
    for resto in restaurantes_locales:
        mesas_aptas = db.query(models.Mesa).filter(
            models.Mesa.restaurante_id == resto.id,
            models.Mesa.capacidad_max >= personas
        ).all()
        
        # Si el restaurante tiene infraestructura física para ese número de personas, lo añadimos como opción disponible
        if mesas_aptas:
            resultado_busqueda.append({
                "restaurante_id": resto.id,
                "nombre": resto.nombre,
                "ciudad": resto.ciudad,
                "estado": resto.estado,
                "tipo_cocina": resto.tipo_cocina,
                "mesas_compatibles_zonas": list(set([m.zona for m in mesas_aptas])) # Lista de zonas disponibles (Terraza, Salón, etc.)
            })

    return {
        "status": "success",
        "criterio": f"Búsqueda en '{ciudad}' para un grupo de {personas} personas.",
        "total_opciones_encontradas": len(resultado_busqueda),
        "restaurantes_disponibles": resultado_busqueda
    }
    
    
# 🔄 RUTA DE ACTUALIZACIÓN (PATCH): Cambiar el estatus de una reserva (Confirmada / Asistió / Cancelada)
@app.patch("/reservas/{reserva_id}")
def actualizar_estatus_reserva(reserva_id: int, actualizacion: schemas.ReservaStatusUpdate, db: Session = Depends(obtener_db)):
    # 1. Buscamos si la reserva existe físicamente en la base de datos local
    reserva_existente = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    
    if not reserva_existente:
        raise HTTPException(
            status_code=404, 
            detail=f"🚫 ERROR: No se encontró ninguna reservación con el ID {reserva_id} en el sistema."
        )
    
    # 2. Validamos que el estatus ingresado sea uno de los oficiales de la plataforma
    estatus_limpio = actualizacion.status.strip().capitalize()
    if estatus_limpio not in ["Confirmada", "Asistió", "Cancelada"]:
        raise HTTPException(
            status_code=400, 
            detail="🚫 Estatus inválido. Use únicamente: 'Confirmada', 'Asistió' o 'Cancelada'."
        )
    
    # 3. Aplicamos el cambio de estatus en mesa_mexico.db
    reserva_existente.status = estatus_limpio
    db.commit()             # Guardamos los cambios físicamente en el disco duro
    db.refresh(reserva_existente)
    
    return {
        "status": "success",
        "mensaje": f"¡Éxito! La reservación número {reserva_existente.id} ha sido actualizada a '{reserva_existente.status}'.",
        "data": {
            "reserva_id": reserva_existente.id,
            "restaurante": reserva_existente.restaurante.nombre,
            "mesa_asignada": reserva_existente.mesa.numero_mesa,
            "nuevo_status": reserva_existente.status
        }
    }         
    
    
# 🗑️ RUTA DE ELIMINACIÓN (DELETE): Dar de baja un restaurante y limpiar su inventario físico
@app.delete("/restaurantes/{restaurante_id}")
def eliminar_restaurante_sistema(restaurante_id: int, db: Session = Depends(obtener_db)):
    # 1. Buscamos si el restaurante existe físicamente en la base de datos
    restaurante_existente = db.query(models.Restaurante).filter(models.Restaurante.id == restaurante_id).first()
    
    if not restaurante_existente:
        raise HTTPException(
            status_code=404, 
            detail=f"🚫 ERROR: No se encontró ningún restaurante registrado con el ID {restaurante_id}."
        )
    
    # Guardamos el nombre temporalmente antes de borrarlo para el mensaje de éxito
    nombre_borrado = restaurante_existente.nombre
    ciudad_borrada = restaurante_existente.ciudad
    
    # 2. Ejecutamos la baja física en la base de datos local
    db.delete(restaurante_existente)
    db.commit()  # SQL ejecuta la cascada y borra mesas y reservas de este negocio automáticamente
    
    return {
        "status": "success",
        "mensaje": f"¡BAJA COMPLETADA! El restaurante '{nombre_borrado}' de {ciudad_borrada} y todo su inventario de mesas/reservas han sido eliminados de forma permanente de la plataforma nacional."
    }    
    
    
    