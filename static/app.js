async function ejecutarBusquedaReal() {
    const ciudad = document.getElementById('input-ciudad').value.trim();
    const personas = document.getElementById('select-personas').value;
    const contenedor = document.getElementById('contenedor-resultados');

    if (!ciudad) {
        alert("Por favor, escribe el nombre de una ciudad de México.");
        return;
    }

    contenedor.innerHTML = '<div class="alerta-vacia">Buscando mesas libres en la base de datos local...</div>';

    try {
        const respuesta = await fetch(`http://127.0.0{encodeURIComponent(ciudad)}&personas=${personas}`);
        const resultado = await respuesta.json();

        contenedor.innerHTML = '';

        if (resultado.status === "success" && resultado.restaurantes_disponibles) {
            if (resultado.restaurantes_disponibles.length === 0) {
                contenedor.innerHTML = `<div class="alerta-vacia">No se encontraron restaurantes con mesas disponibles para ${personas} personas en '${ciudad}'.</div>`;
                return;
            }
            resultado.restaurantes_disponibles.forEach(resto => {
                const tarjeta = document.createElement('div');
                tarjeta.className = 'tarjeta-restaurante';
                tarjeta.innerHTML = `
                    <h3>${resto.nombre}</h3>
                    <span class="badge-cocina">${resto.tipo_cocina}</span>
                    <p class="info-localizacion">📍 ${resto.ciudad}, ${resto.estado}</p>
                    <p class="zonas-disponibles">✅ Zonas libres: ${resto.mesas_compatibles_zonas.join(', ')}</p>
                `;
                contenedor.appendChild(tarjeta);
            });
        }
    } catch (error) {
        console.error(error);
        contenedor.innerHTML = '<div class="alerta-vacia">❌ Error de conexión: Asegúrate de que el servidor local esté encendido.</div>';
    }
}


