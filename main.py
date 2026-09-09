from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy.orm import Session
import database, models, schemas
import datetime as dt

app = FastAPI(title="Mesa México - API SaaS")

# 🔌 Configuración de CORS para evitar bloqueos de red
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📂 Montar la carpeta static para los archivos CSS y JS
app.mount("/static", StaticFiles(directory="static"), name="static")

def obtener_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🏠 VISTA PRINCIPAL: Cargar la pantalla web
@app.get("/")
def leer_raiz():
    return FileResponse("index.html")

# 🔍 MOTOR DE BÚSQUEDA DINÁMICO: Consulta real en las celdas de mesa_mexico.db
@app.get("/buscar")
def buscar_restaurantes_disponibles(ciudad: str, personas: int = 4, db: Session = Depends(obtener_db)):
    # 1. Buscamos en las tablas todos los restaurantes que coincidan con la ciudad de forma elástica
    ciudad_limpia = ciudad.lower().strip()
    restaurantes = db.query(models.Restaurante).filter(models.Restaurante.ciudad.ilike(f"%{ciudad_limpia}%")).all()
    
    lista_respuesta = []
    
    # 2. Mapeamos cada restaurante encontrado en el disco duro con sus datos reales
    for resto in restaurantes:
        # Jalamos sus zonas de mesas compatibles desde la columna capacidad_max
        mesas_validas = db.query(models.Mesa).filter(
            models.Mesa.restaurante_id == resto.id,
            models.Mesa.capacidad_max >= personas
        ).all()
        
        zonas_libres = list(set([m.zona for m in mesas_validas])) if mesas_validas else ["Terraza"]
        
        # 🖼️ DIRECCIÓN MULTIMEDIA INTELIGENTE: Si la celda está vacía, asigna fotos reales .jpg
        foto_default = "https://unsplash.com"
        if "mariscos" in resto.nombre.lower():
            foto_default = "https://unsplash.com" # Mariscos Riviera

        lista_respuesta.append({
            "id": resto.id,
            "nombre": resto.nombre,
            "tipo_cocina": resto.tipo_cocina,
            "ciudad": resto.ciudad,
            "estado": resto.estado,
            "imagen_url": resto.imagen_url if resto.imagen_url else foto_default,  # 👈 Usa la foto real o el respaldo premium
            "sitio_web": resto.sitio_web,
            "mesas_compatibles_zonas": zonas_libres
        })

        
    return {
        "status": "success",
        "restaurantes_disponibles": lista_respuesta
    }



# 🔑 LOGIN DIARIO REAL: Validación desde las celdas del .db
@app.get("/clientes/login")
@app.post("/clientes/login")
def login_diario_cliente(credenciales: schemas.ClienteLogin, db: Session = Depends(obtener_db)):
    correo_limpio = credenciales.correo.lower().strip()
    cliente = db.query(models.Cliente).filter(models.Cliente.correo == correo_limpio).first()
    
    if not cliente or cliente.password != credenciales.password:
        raise HTTPException(status_code=401, detail="🚫 Credenciales incorrectas.")
        
    return {
        "status": "success",
        "mensaje": f"¡Inicio de sesión exitoso! Bienvenido, {cliente.nombre}.",
        "cliente": { "id": cliente.id, "nombre": cliente.nombre, "correo": cliente.correo }
    }

# 🏢 REGISTRO DE SOCIOS COMERCIALES (EMPRESAS)
@app.post("/empresa/registrar")
def registrar_cuenta_empresarial(cliente: schemas.ClienteCreate, db: Session = Depends(obtener_db)):
    correo_limpio = cliente.correo.lower().strip()
    existe = db.query(models.Cliente).filter(models.Cliente.correo == correo_limpio).first()
    
    if existe:
        raise HTTPException(status_code=400, detail="🚫 ERROR: Este correo de empresa ya existe.")

    nueva_empresa = models.Cliente(
        nombre=cliente.nombre,
        telefono=cliente.telefono,
        correo=correo_limpio,
        password=cliente.password,
        rol="empresa",
        verificado=True
    )
    db.add(nueva_empresa)
    db.commit()
    db.refresh(nueva_empresa)
    return {
        "status": "success",
        "mensaje": f"¡Cuenta empresarial de '{cliente.nombre}' creada con éxito!",
        "empresa_id": nueva_empresa.id
    }

# 🖼️ ALTA DE RESTAURANTE REAL (CONEXIÓN RELACIONAL COMPLETA)
@app.post("/restaurantes/crear")
def crear_restaurante_empresarial(restaurante: schemas.RestauranteCreate, empresa_id: int, db: Session = Depends(obtener_db)):
    dueno = db.query(models.Cliente).filter(models.Cliente.id == empresa_id, models.Cliente.rol == "empresa").first()
    if not dueno:
        raise HTTPException(status_code=403, detail="🔒 ACCESO DENEGADO: ID de empresa no válido.")

    nuevo_local = models.Restaurante(
        nombre=restaurante.nombre,
        ciudad=restaurante.ciudad,
        estado=restaurante.estado,
        tipo_cocina=restaurante.tipo_cocina,
        imagen_url=restaurante.imagen_url,
        sitio_web=restaurante.sitio_web,
        dueno_id=empresa_id,
        activo=True
    )
    db.add(nuevo_local)
    db.commit()
    db.refresh(nuevo_local)
    
    primera_mesa = models.Mesa(
        numero_mesa="1",
        capacidad_max=4,
        zona="Terraza",
        restaurante_id=nuevo_local.id
    )
    db.add(primera_mesa)
    db.commit()
    return {
        "status": "success",
        "restaurantes_disponibles": f"¡El restaurante '{restaurante.nombre}' ha sido dado de alta con éxito!",
        "restaurante_id": nuevo_local.id
    }

# 📅 MOTOR RELACIONAL MULTIUSUARIO: Lógica dinámica con módulo antichoque de 2 horas
@app.post("/reservas/rapida")
def crear_reserva_rapida_horario(restaurante_id: int, hora_texto: str, cliente_correo: str, db: Session = Depends(obtener_db)):
    cliente = db.query(models.Cliente).filter(models.Cliente.correo == cliente_correo.lower().strip()).first()
    if not cliente:
        return PlainTextResponse("🔒 ACCESO RESTRINGIDO: Inicia sesión.", status_code=401)

    if "7:00" in hora_texto: hora_solicitada = dt.time(19, 0)
    elif "7:15" in hora_texto: hora_solicitada = dt.time(19, 15)
    else: hora_solicitada = dt.time(19, 30)

    fecha_hoy = dt.date.today()
    personas_reserva = 4

    mesas_candidatas = db.query(models.Mesa).filter(
        models.Mesa.restaurante_id == restaurante_id,
        models.Mesa.capacidad_max >= personas_reserva
    ).all()

    if not mesas_candidatas:
        return PlainTextResponse("🚫 ERROR: Este restaurante no tiene mesas configuradas.", status_code=400)

    mesa_asignada = None

    for mesa in mesas_candidatas:
        reservas_existentes = db.query(models.Reserva).filter(
            models.Reserva.mesa_id == mesa.id,
            models.Reserva.fecha == fecha_hoy,
            models.Reserva.status == "Confirmada"
        ).all()

        colision_detectada = False
        for res in reservas_existentes:
            dt_existente = dt.datetime.combine(fecha_hoy, res.hora)
            dt_solicitado = dt.datetime.combine(fecha_hoy, hora_solicitada)
            diferencia_minutos = abs((dt_solicitado - dt_existente).total_seconds()) / 60

            if diferencia_minutos < 120:
                colision_detectada = True
                break

        if not colision_detectada:
            mesa_asignada = mesa
            break

    if not mesa_asignada:
        return PlainTextResponse(f"🚫 CHOQUE DE HORARIOS: La mesa ya se encuentra ocupada dentro del rango de protección de 2 horas. Intenta otro bloque.", status_code=400)

    nueva_reserva = models.Reserva(
        restaurante_id=restaurante_id,
        mesa_id=mesa_asignada.id,
        cliente_id=cliente.id,
        fecha=fecha_hoy,
        hora=hora_solicitada,
        num_comensales=personas_reserva,
        status="Confirmada"
    )

    db.add(nueva_reserva)
    db.commit()

    return PlainTextResponse(f"¡RESERVACIÓN CONFIRMADA REAL! Mesa {mesa_asignada.numero_mesa} ({mesa_asignada.zona}) asignada con éxito para las {hora_texto} a nombre de {cliente.nombre}.", status_code=200)
