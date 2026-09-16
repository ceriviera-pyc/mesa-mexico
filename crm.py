import datetime as dt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import obtener_db
import models

# 🔌 Creamos el enrutador del CRM con un prefijo automático
# Esto significa que todas las rutas que escribamos aquí empezarán con "/api/crm"
router = APIRouter(prefix="/api/crm", tags=["Módulos del CRM Administrativo"])

# 📊 CONTROL DE MANDOS CRM: Obtiene el listado completo de reservas con datos cruzados
@router.get("/reservas")
def obtener_todas_las_reservas_crm(db: Session = Depends(obtener_db)):
    # 1. Consultamos todas las reservas guardadas en el archivo SQLite
    reservas_db = db.query(models.Reserva).all()
    
    lista_crm = []
    
    # 2. LÓGICA DE CRUCE: Extraemos información de las relaciones de cada reserva
    for res in reservas_db:
        nombre_cliente = res.cliente.nombre if res.cliente else "Comensal Anónimo"
        telefono_cliente = res.cliente.telefono if res.cliente else "Sin Teléfono"
        nombre_resto = res.restaurante.nombre if res.restaurante else "Local Removido"
        num_mesa = res.mesa.numero_mesa if res.mesa else "Sin Asignar"
        zona_mesa = res.mesa.zona if res.mesa else "Salón"
        
        # 3. EMPAQUETAMOS EL REGISTRO CRM
        lista_crm.append({
            "reserva_id": res.id,
            "restaurante": nombre_resto,
            "cliente": {
                "nombre": nombre_cliente,
                "telefono": telefono_cliente,
                "correo": res.cliente.correo if res.cliente else ""
            },
            "mesa": {
                "numero": num_mesa,
                "zona": zona_mesa
            },
            "fecha": str(res.fecha),
            "hora": res.hora.strftime("%H:%M") if res.hora else "00:00",
            "comensales": res.num_comensales,
            "status": res.status,
            "notas": res.notas if res.notas else "",
            "creada_el": res.creado_en.strftime("%d/%m/%Y %H:%M") if res.creado_en else ""
        })
        
    return {
        "status": "success",
        "total_registros": len(lista_crm),
        "datos_crm": lista_crm
    }
