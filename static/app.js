// 🧠 VARIABLE GLOBAL DE RESPALDO PARA NAVEGACIÓN INPRIVATE / INCÓGNITO (SINCRONIZADA)
let sesionMemoriaRam = {
    nombre: localStorage.getItem("usuario_nombre") || null,
    correo: localStorage.getItem("usuario_correo") || null,
    id: localStorage.getItem("usuario_id") || null
};
let empresaActivaId = null; // Guardará el ID de la empresa al iniciar sesión

document.addEventListener("DOMContentLoaded", () => {
    actualizarInterfazUsuarioNav();
});

// 💼 FUNCIONES DE CONTROL VISUAL PARA SOCIOS COMERCIALES (EMPRESAS)
function abrirModalEmpresa() {
    document.getElementById('modal-empresa').style.display = 'flex';
    cambiarTabEmpresa('login');
}

function cerrarModalEmpresa() {
    document.getElementById('modal-empresa').style.display = 'none';
}

function cerrarModalAltaRestaurante() {
    document.getElementById('modal-alta-restaurante').style.display = 'none';
}

function cambiarTabEmpresa(pestaña) {
    const tabLogin = document.getElementById('tab-empresa-login');
    const tabReg = document.getElementById('tab-empresa-registro');
    const formLogin = document.getElementById('form-empresa-login');
    const formReg = document.getElementById('form-empresa-registro');

    if (pestaña === 'login') {
        tabLogin.className = 'tab-link activo';
        tabReg.className = 'tab-link';
        formLogin.className = 'formulario-bloque activo';
        formReg.className = 'formulario-bloque';
    } else {
        tabLogin.className = 'tab-link';
        tabReg.className = 'tab-link activo';
        formLogin.className = 'formulario-bloque';
        formReg.className = 'formulario-bloque activo';
    }
}

// 🏢 1. DISPARAR REGISTRO ASÍNCRONO DE SOCIO COMERCIAL (CON PREFIJO /API)
async function ejecutarRegistroEmpresa() {
    const nombre = document.getElementById('empresa-reg-nombre').value.trim();
    const telefono = document.getElementById('empresa-reg-telefono').value.trim();
    const correo = document.getElementById('empresa-reg-correo').value.trim();
    const password = document.getElementById('empresa-reg-password').value;

    if (!nombre || !correo || !password) {
        alert("Por favor, llena los campos corporativos obligatorios.");
        return;
    }

    try {
        const respuesta = await fetch('/api/empresa/registrar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre, telefono, correo, password })
        });
        const resultado = await respuesta.json();

        if (respuesta.status === 200 && resultado.status === "success") {
            alert(resultado.mensaje);
            cambiarTabEmpresa('login');
            document.getElementById('empresa-login-correo').value = correo;
        } else {
            alert(resultado.detail || "Error al crear la cuenta empresarial.");
        }
    } catch (error) {
        alert("❌ Error de comunicación al registrar la empresa.");
    }
}


// 🔑 2. DISPARAR INICIO DE SESIÓN CORPORATIVO (CON PREFIJO /API)
async function ejecutarLoginEmpresa() {
    const correo = document.getElementById('empresa-login-correo').value.trim();
    const password = document.getElementById('empresa-login-password').value;

    try {
        const respuesta = await fetch('/api/clientes/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ correo, password })
        });
        const resultado = await respuesta.json();

        if (respuesta.status === 200 && resultado.status === "success") {
            empresaActivaId = resultado.cliente.id;
            cerrarModalEmpresa();
            document.getElementById('modal-alta-restaurante').style.display = 'flex';
            alert(`💼 ¡BIENVENIDO AL PANEL DE CONTROL!\n\n${resultado.mensaje}`);
        } else {
            alert(resultado.detail || "🚫 Acceso denegado. Verifica las credenciales de la empresa.");
        }
    } catch (error) {
        alert("❌ Error de conexión al verificar el socio.");
    }
}

// 🚀 3. SUBIDA REAL DE RESTAURANTE CON IMÁGENES A LA BASE DE DATOS (CON PREFIJO /API)
async function ejecutarAltaRestauranteReal() {
    const nombre = document.getElementById('resto-nombre').value.trim();
    const cocina = document.getElementById('resto-cocina').value.trim();
    const ciudad = document.getElementById('resto-ciudad').value.trim();
    const estado = document.getElementById('resto-estado').value.trim();
    const imagenUrl = document.getElementById('resto-imagen').value.trim();
    const sitioWeb = document.getElementById('resto-web').value.trim();

    if (!nombre || !ciudad || !estado) {
        alert("Por favor, introduce el nombre del local y su ubicación.");
        return;
    }

    try {
        const respuesta = await fetch(`/api/restaurantes/crear?empresa_id=${empresaActivaId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nombre: nombre,
                ciudad: ciudad,
                estado: estado,
                tipo_cocina: cocina || "Mexicana",
                imagen_url: imagenUrl || "/static/imagenes/defecto.jpg",
                sitio_web: sitioWeb || null
            })
        });
        const resultado = await respuesta.json();

        if (respuesta.status === 200 && resultado.status === "success") {
            alert(resultado.mensaje);
            cerrarModalAltaRestaurante();
            ejecutarBusquedaReal(); 
        } else {
            alert(resultado.detail || "No se pudo registrar el restaurante.");
        }
    } catch (error) {
        alert("❌ Error de red al intentar subir el negocio.");
    }
}

// 👥 CONTROLES DEL MODAL DE COMENSALES ORDINARIOS
function abrirModalSesion(pestaña) { 
    document.getElementById('modal-sesion').style.display = 'flex'; 
    cambiarPestañaModal(pestaña); 
}

function cerrarModalSesion() { 
    document.getElementById('modal-sesion').style.display = 'none'; 
}

function cambiarPestañaModal(pestaña) {
    const tabLogin = document.getElementById('tab-login'); 
    const tabRegistro = document.getElementById('tab-registro');
    const formLogin = document.getElementById('form-login'); 
    const formRegistro = document.getElementById('form-registro');
    
    if (pestaña === 'login') { 
        tabLogin.className = 'tab-link activo'; 
        tabRegistro.className = 'tab-link'; 
        formLogin.className = 'formulario-bloque activo'; 
        formRegistro.className = 'formulario-bloque'; 
    } else { 
        tabLogin.className = 'tab-link'; 
        tabRegistro.className = 'tab-link activo'; 
        formLogin.className = 'formulario-bloque'; 
        formRegistro.className = 'formulario-bloque activo'; 
    }
}

// 🔑 3. DISPARAR INICIO DE SESIÓN DE CLIENTE (CON PREFIJO /API)
async function ejecutarLoginDiario() {
    const correo = document.getElementById('login-correo').value.trim();
    const password = document.getElementById('login-password').value;

    if (!correo || !password) {
        alert("Por favor, completa todos los campos.");
        return;
    }

    try {
        const response = await fetch('/api/clientes/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ correo: correo, password: password })
        });

        const resultado = await response.json();

        if (response.status === 200 && resultado.status === "success") {
            localStorage.setItem("usuario_nombre", resultado.cliente.nombre);
            localStorage.setItem("usuario_correo", resultado.cliente.correo);
            localStorage.setItem("usuario_id", resultado.cliente.id);

            sesionMemoriaRam.nombre = resultado.cliente.nombre;
            sesionMemoriaRam.correo = resultado.cliente.correo;
            sesionMemoriaRam.id = resultado.cliente.id;

            cerrarModalSesion();
            actualizarInterfazUsuarioNav();
            alert(resultado.mensaje || "¡Inicio de sesión exitoso!");
            window.location.reload();
        } else {
            alert(resultado.detail || "Correo o contraseña incorrectos.");
        }
    } catch (e) {
        console.error("Error en la autenticación:", e);
        alert("Hubo un problema de conexión con el servidor de Mesa México.");
    }
}

// 👤 4. DISPARAR SOLICITUD DE PIN DE PRE-REGISTRO (CON PREFIJO /API)
async function ejecutarPreRegistro() {
    const nombre = document.getElementById('reg-nombre').value.trim();
    const telefono = document.getElementById('reg-telefono').value.trim();
    const correo = document.getElementById('reg-correo').value.trim();
    const password = document.getElementById('reg-password').value;

    if (!nombre || !telefono || !correo || !password) {
        alert("Todos los campos son obligatorios para el registro.");
        return;
    }

    try {
        const response = await fetch('/api/clientes/pre-registro', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                nombre: nombre, 
                telefono: telefono, 
                correo: correo, 
                password: password 
            })
        });

        const resultado = await response.json();

        if (response.status === 200) {
            alert("¡Código de activación generado! Introduce el PIN impreso en la terminal de tu VS Code.");
            document.getElementById('bloque-datos-registro').style.display = 'none';
            document.getElementById('bloque-verificar-pin').style.display = 'flex';
        } else {
            alert(resultado.detail || "No se pudo procesar el pre-registro.");
        }
    } catch (e) {
        console.error("Error en pre-registro:", e);
        alert("Fallo de conexión con el backend.");
    }
}

// 🔐 5. DISPARAR ACTIVACIÓN REAL CON EL PIN DE 6 DÍGITOS (CON PREFIJO /API)
async function ejecutarVerificacionUnica() {
    const correo = document.getElementById('reg-correo').value.trim();
    const pin = document.getElementById('reg-pin').value.trim();

    if (!pin) {
        alert("Por favor, introduce el PIN de activación.");
        return;
    }

    try {
        const response = await fetch('/api/clientes/verificar-pin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ correo: correo, codigo: pin })
        });

        const resultado = await response.json();

        if (response.status === 200 && resultado.status === "success") {
            alert("¡Cuenta verificada y activada con éxito!");
            cambiarPestañaModal('login');
            document.getElementById('login-correo').value = correo;
            document.getElementById('bloque-datos-registro').style.display = 'flex';
            document.getElementById('bloque-verificar-pin').style.display = 'none';
        } else {
            alert(resultado.detail || "El PIN introducido es incorrecto o ya expiró.");
        }
    } catch (e) {
        console.error("Error al verificar PIN:", e);
        alert("Error de conexión al activar tu cuenta.");
    }
}

function ejecutarLogout() { 
    localStorage.clear(); 
    sesionMemoriaRam.nombre = null; 
    sesionMemoriaRam.correo = null; 
    sesionMemoriaRam.id = null;
    actualizarInterfazUsuarioNav(); 
    document.getElementById('contenedor-resultados').innerHTML = '<div class="alerta-vacia">Inicia sesión para consultar las mesas libres.</div>';
    alert("Sesión cerrada."); 
}

function actualizarInterfazUsuarioNav() {
    const nav = document.getElementById('bloque-autenticacion-nav'); 
    const usuarioNombre = sesionMemoriaRam.nombre;
    if (usuarioNombre) { 
        nav.innerHTML = `<div style="display:flex; gap:1.2rem; align-items:center;"><p style="font-size:0.95rem; color:white; font-weight:600;">👤 Hola, <span style="color:#10b981;">${usuarioNombre}</span></p><button class="btn-nav" style="border-color:#da3743; color:#da3743;" onclick="ejecutarLogout()">Salir</button></div>`; 
    } else { 
        nav.innerHTML = `<button class="btn-nav" onclick="abrirModalSesion('login')">Iniciar Sesión</button><button class="btn-nav btn-nav-primario" onclick="abrirModalSesion('registro')">Crear Cuenta</button>`; 
    }
}

// 🏢 MOTOR DE BÚSQUEDA REDISEÑADO ESTILO OPENTABLE
async function ejecutarBusquedaReal() {
    const ciudad = document.getElementById('busqueda-input').value.trim(); 
    const personas = document.getElementById('select-personas').value; 
    const contenedor = document.getElementById('contenedor-resultados');
    if (!ciudad) return;
    contenedor.innerHTML = '<div class="alerta-vacia">Buscando mesas libres...</div>';
    try {
        const respuesta = await fetch(`/api/buscar?ciudad=${encodeURIComponent(ciudad)}&personas=${personas}`); 
        const resultado = await respuesta.json(); 
        contenedor.innerHTML = '';
        const listaRestaurantes = resultado.restaurantes_disponibles || [];
        if (listaRestaurantes.length > 0) {
            listaRestaurantes.forEach(resto => {
                const tarjeta = document.createElement('div'); 
                tarjeta.className = 'tarjeta-restaurante';
                
                const nombreLocal = resto.nombre || "Restaurante Corporativo";
                const cocinaLocal = resto.tipo_cocina || "Especialidad";
                const ciudadLocal = resto.ciudad || ciudad;
                const idLocal = resto.id || 1;

                let fotoFinal = "/static/imagenes/defecto.jpg";
                if (nombreLocal.toLowerCase().includes('piaggia')) {
                    fotoFinal = "/static/imagenes/piaggia.jpg";
                } else if (nombreLocal.toLowerCase().includes('mariscos')) {
                    fotoFinal = "/static/imagenes/mariscos.jpg";
                }

                tarjeta.innerHTML = `
                    <div class="foto-contenedor" style="background-image: url('${fotoFinal}') !important; display: block !important;"></div>
                    <div class="cuerpo-tarjeta">
                        <h3>${nombreLocal}</h3>
                        <div class="info-meta"><span>${cocinaLocal}</span> • <span>${ciudadLocal}</span></div>
                        <div class="bloque-horarios">
                            <button class="btn-horario" onclick="solicitarMesaHorarioRapido(${idLocal}, '7:30 PM', ${personas})">7:30 pm</button>
                        </div>
                    </div>
                `;
                contenedor.appendChild(tarjeta);
            });
        } else { 
            contenedor.innerHTML = '<div class="alerta-vacia">No se encontraron restaurantes con mesas libres en esta ciudad.</div>'; 
        }
    } catch (error) { 
        contenedor.innerHTML = '<div class="alerta-vacia">❌ Error de conexión al buscar en la base de datos.</div>'; 
    }
}

// Vinculamos el clic del botón ¡Vamos! al motor de búsqueda
document.getElementById('btn-vamos').addEventListener('click', ejecutarBusquedaReal);

// -------------------------------------------------------------
// Bloque de geolocalización elástico para static/app.js
// -------------------------------------------------------------
document.getElementById('btn-actualizar-ubicacion').addEventListener('click', () => {
    if (!navigator.geolocation) {
        alert("Tu navegador no soporta la geolocalización.");
        return;
    }

    const btn = document.getElementById('btn-actualizar-ubicacion');
    const textoOriginal = btn.innerText;
    btn.innerText = "Buscando satélites...";
    btn.disabled = true;

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const coordenadas = {
                latitud: position.coords.latitude,
                longitud: position.coords.longitude
            };

            console.log("Coordenadas obtenidas:", coordenadas);
            const urlApi = '/api/ubicacion/actualizar';

            fetch(urlApi, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(coordenadas)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Error en la respuesta del servidor");
                }
                return response.json();
            })
            .then(data => {
                alert("¡Ubicación actualizada con éxito en la base de datos!");
                console.log("Respuesta de FastAPI:", data);
                // 👈 ESTA ES LA LÍNEA NUEVA QUE RELLENA TU CAJA DE BÚSQUEDA AL INSTANTE
                document.getElementById('busqueda-input').value = "Playa del Carmen";
                btn.innerText = textoOriginal;
                btn.disabled = false;
            })
            .catch(err => {
                console.error("Error al sincronizar coordenadas:", err);
                alert("Se obtuvo la ubicación local, pero falló al sincronizar con el servidor.");
                btn.innerText = textoOriginal;
                btn.disabled = false;
            });
        },
        (error) => {
            console.error("Error de GPS:", error);
            btn.innerText = textoOriginal;
            btn.disabled = false;
            if (error.code === error.PERMISSION_DENIED) {
                alert("Por favor, permite el acceso a la ubicación en tu navegador.");
            } else {
                alert("No se pudo obtener tu ubicación: " + error.message);
            }
        },
        {
            enableHighAccuracy: false,
            timeout: 15000,
            maximumAge: 60000
        }
    );
});

